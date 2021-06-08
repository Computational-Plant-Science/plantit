import binascii
import fileinput
import json
import logging
import os
import sys
import uuid
from datetime import timedelta, datetime
from math import ceil
from os import environ
from os.path import join, isdir
from pathlib import Path
from typing import List

import yaml
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from dateutil import parser
from django.contrib.auth.models import User
from django.utils import timezone

from plantit import settings
from plantit.agents.models import Agent, AgentAccessPolicy, AgentRole, AgentExecutor
from plantit.agents.utils import map_agent
from plantit.docker import parse_image_components, image_exists
from plantit.github import get_repo_config
from plantit.popos import FileInput, Parameter, FilesInput, DirectoryInput, TaskOptions, BindMount
from plantit.redis import RedisClient
from plantit.ssh import SSH, execute_command
from plantit.tasks.models import Task, DelayedTask, RepeatingTask, TaskStatus, JobQueueTask
from plantit.utils import parse_bind_mount, format_bind_mount
from plantit.workflows.utils import map_old_workflow_config_to_new

logger = logging.getLogger(__name__)


def stat_logs(id: str):
    log_path = Path(join(environ.get('RUNS_LOGS'), f"{id}.plantit.log"))
    return datetime.fromtimestamp(log_path.stat().st_mtime) if log_path.is_file() else None


def remove_logs(id: str, agent: str):
    local_log_path = join(environ.get('RUNS_LOGS'), f"{id}.plantit.log")
    # agent_log_path = join(environ.get('RUNS_LOGS'), f"{id}.{agent.lower()}.log")
    os.remove(local_log_path)
    # os.remove(agent_log_path)


def parse_walltime(walltime) -> timedelta:
    time_split = walltime.split(':')
    time_hours = int(time_split[0])
    time_minutes = int(time_split[1])
    time_seconds = int(time_split[2])
    return timedelta(hours=time_hours, minutes=time_minutes, seconds=time_seconds)


def parse_job_id(line: str) -> str:
    try:
        return str(int(line.replace('Submitted batch job', '').strip()))
    except:
        raise Exception(f"Failed to parse job ID from: '{line}'")


def parse_time(data: dict) -> datetime:
    time_str = data['time']
    time = parser.isoparse(time_str)
    return time


def parse_eta(data: dict) -> (datetime, int):
    delay_value = data['delayValue']
    delay_units = data['delayUnits']

    if delay_units == 'Seconds':
        seconds = int(delay_value)
    elif delay_units == 'Minutes':
        seconds = int(delay_value) * 60
    elif delay_units == 'Hours':
        seconds = int(delay_value) * 60 * 60
    elif delay_units == 'Days':
        seconds = int(delay_value) * 60 * 60 * 24
    else:
        raise ValueError(f"Unsupported delay units (expected: Seconds, Minutes, Hours, or Days)")

    now = timezone.now()
    eta = now + timedelta(seconds=seconds)

    return eta, seconds


def parse_task_config(config: dict) -> (List[str], TaskOptions):
    errors = []
    image = None
    if not isinstance(config['image'], str):
        errors.append('Attribute \'image\' must not be a str')
    elif config['image'] == '':
        errors.append('Attribute \'image\' must not be empty')
    else:
        image = config['image']
        if 'docker' in image:
            image_owner, image_name, image_tag = parse_image_components(image)
            if not image_exists(image_name, image_owner, image_tag):
                errors.append(f"Image '{image}' not found on Docker Hub")

    work_dir = None
    if not isinstance(config['workdir'], str):
        errors.append('Attribute \'workdir\' must not be a str')
    elif config['workdir'] == '':
        errors.append('Attribute \'workdir\' must not be empty')
    else:
        work_dir = config['workdir']

    command = None
    if not isinstance(config['command'], str):
        errors.append('Attribute \'command\' must not be a str')
    elif config['command'] == '':
        errors.append('Attribute \'command\' must not be empty')
    else:
        command = config['command']

    parameters = None
    if 'parameters' in config:
        if not all(['key' in param and
                    param['key'] is not None and
                    param['key'] != '' and
                    'value' in param and
                    param['value'] is not None and
                    param['value'] != ''
                    for param in config['parameters']]):
            errors.append('Every parameter must have a non-empty \'key\' and \'value\'')
        else:
            parameters = [Parameter(param['key'], param['value']) for param in config['parameters']]

    bind_mounts = None
    if 'bind_mounts' in config:
        if not all(mount_point != '' for mount_point in config['bind_mounts']):
            errors.append('Every mount point must be non-empty')
        else:
            bind_mounts = [parse_bind_mount(work_dir, mount_point) for mount_point in config['bind_mounts']]

    input = None
    if 'input' in config:
        if 'file' in config['input']:
            if 'path' not in config['input']['file']:
                errors.append('Section \'file\' must include attribute \'path\'')
            input = FileInput(path=config['input']['file']['path'])
        elif 'files' in config['input']:
            if 'path' not in config['input']['files']:
                errors.append('Section \'files\' must include attribute \'path\'')
            input = FilesInput(
                path=config['input']['files']['path'],
                patterns=config['input']['files']['patterns'] if 'patterns' in config['input']['files'] else None)
        elif 'directory' in config['input']:
            if 'path' not in config['input']['directory']:
                errors.append('Section \'directory\' must include attribute \'path\'')
            input = DirectoryInput(path=config['input']['directory']['path'])
        else:
            errors.append('Section \'input\' must include a \'file\', \'files\', or \'directory\' section')

    log_file = None
    if 'log_file' in config:
        log_file = config['log_file']
        if not isinstance(log_file, str):
            errors.append('Attribute \'log_file\' must be a str')
        elif log_file.rpartition('/')[0] != '' and not isdir(log_file.rpartition('/')[0]):
            errors.append('Attribute \'log_file\' must be a valid file path')

    no_cache = None
    if 'no_cache' in config:
        no_cache = config['no_cache']
        if not isinstance(no_cache, bool):
            errors.append('Attribute \'no_cache\' must be a bool')

    gpu = None
    if 'gpu' in config:
        gpu = config['gpu']
        if not isinstance(gpu, bool):
            errors.append('Attribute \'gpu\' must be a bool')

    jobqueue = None
    if 'jobqueue' in config:
        jobqueue = config['jobqueue']
        if not (
                'slurm' in jobqueue or 'yarn' in jobqueue or 'pbs' in jobqueue or 'moab' in jobqueue or 'sge' in jobqueue or 'lsf' in jobqueue or 'oar' in jobqueue or 'kube' in jobqueue):
            raise ValueError(f"Unsupported jobqueue configuration: {jobqueue}")

        if 'queue' in jobqueue:
            if not isinstance(jobqueue['queue'], str):
                errors.append('Section \'jobqueue\'.\'queue\' must be a str')
        if 'project' in jobqueue:
            if not isinstance(jobqueue['project'], str):
                errors.append('Section \'jobqueue\'.\'project\' must be a str')
        if 'walltime' in jobqueue:
            if not isinstance(jobqueue['walltime'], str):
                errors.append('Section \'jobqueue\'.\'walltime\' must be a str')
        if 'cores' in jobqueue:
            if not isinstance(jobqueue['cores'], int):
                errors.append('Section \'jobqueue\'.\'cores\' must be a int')
        if 'processes' in jobqueue:
            if not isinstance(jobqueue['processes'], int):
                errors.append('Section \'jobqueue\'.\'processes\' must be a int')
        if 'extra' in jobqueue and not all(extra is str for extra in jobqueue['extra']):
            errors.append('Section \'jobqueue\'.\'extra\' must be a list of str')
        if 'header_skip' in jobqueue and not all(extra is str for extra in jobqueue['header_skip']):
            errors.append('Section \'jobqueue\'.\'header_skip\' must be a list of str')

    return errors, TaskOptions(
        workdir=work_dir,
        image=image,
        command=command,
        input=input,
        parameters=parameters,
        bind_mounts=bind_mounts,
        # checksums=checksums,
        log_file=log_file,
        jobqueue=jobqueue,
        no_cache=no_cache,
        gpu=gpu)


def prep_command(
        work_dir: str,
        image: str,
        command: str,
        bind_mounts: List[BindMount] = None,
        parameters: List[Parameter] = None,
        docker_username: str = None,
        docker_password: str = None,
        no_cache: bool = False,
        gpu: bool = False) -> str:
    cmd = f"singularity exec --home {work_dir}"

    if bind_mounts is not None:
        if len(bind_mounts) > 0:
            cmd += (' --bind ' + ','.join([format_bind_mount(work_dir, mount_point) for mount_point in bind_mounts]))
        else:
            raise ValueError(f"List expected for `bind_mounts`")

    if parameters is None:
        parameters = []
    parameters.append(Parameter(key='WORKDIR', value=work_dir))
    for parameter in parameters:
        print(f"Replacing '{parameter.key.upper()}' with '{parameter.value}'")
        command = command.replace(f"${parameter.key.upper()}", parameter.value)

    if no_cache:
        cmd += ' --disable-cache'

    if gpu:
        cmd += ' --nv'

    cmd += f" {image} {command}"
    print(f"Using command: '{cmd}'")

    # we don't necessarily want to reveal Docker auth info to the end user, so print the command before adding Docker env variables
    if docker_username is not None and docker_password is not None:
        cmd = f"SINGULARITY_DOCKER_USERNAME={docker_username} SINGULARITY_DOCKER_PASSWORD={docker_password} " + cmd

    return cmd


def create_task(username: str, agent_name: str, workflow: dict, name: str = None) -> Task:
    redis = RedisClient.get()
    repo_name = workflow['repo']['owner']['login']
    repo_owner = workflow['repo']['name']
    repo_config = redis.get(f"workflows/{repo_owner}/{repo_name}")
    if repo_config is None:
        raise ValueError(f"Workflow {repo_owner}/{repo_name} not found")

    agent = Agent.objects.get(name=agent_name)
    user = User.objects.get(username=username)
    guid = str(uuid.uuid4())
    now = timezone.now()

    if agent.executor == AgentExecutor.LOCAL:
        task = Task.objects.create(guid=guid,
                                   name=guid if name is None else name,
                                   user=user,
                                   workflow_owner=repo_name,
                                   workflow_name=repo_owner,
                                   agent=agent,
                                   status=TaskStatus.CREATED,
                                   created=now,
                                   updated=now,
                                   token=binascii.hexlify(os.urandom(20)).decode())
    else:
        task = JobQueueTask.objects.create(guid=guid,
                                           name=guid if name is None else name,
                                           user=user,
                                           workflow_owner=repo_name,
                                           workflow_name=repo_owner,
                                           agent=agent,
                                           status=TaskStatus.CREATED,
                                           created=now,
                                           updated=now,
                                           token=binascii.hexlify(os.urandom(20)).decode())

    # add repo logo
    if 'logo' in repo_config['config']:
        logo_path = repo_config['config']['logo']
        task.workflow_image_url = f"https://raw.githubusercontent.com/{repo_name}/{repo_owner}/master/{logo_path}"

    for tag in workflow['config']['tags']: task.tags.add(tag)     # add task tags
    task.workdir = f"{task.guid}/"                              # use GUID for working directory name
    task.save()
    return task


def upload_task(workflow: dict, task: Task, ssh: SSH, input_files: List[str] = None):
    # update config before uploading
    workflow['config']['workdir'] = join(task.agent.workdir, task.guid)
    workflow['config']['log_file'] = f"{task.guid}.{task.agent.name.lower()}.log"
    if 'output' in workflow['config'] and 'from' in workflow['config']['output']:
        if workflow['config']['output']['from'] is not None and workflow['config']['output']['from'] != '':
            workflow['config']['output']['from'] = join(task.agent.workdir, task.workdir, workflow['config']['output']['from'])

    # if we have outputs, make sure we don't push configuration or job scripts
    if 'output' in workflow['config']:
        workflow['config']['output']['exclude']['names'] = [
            "flow.yaml",
            "template_local_run.sh",
            "template_slurm_run.sh"]

    resources = None if 'resources' not in workflow['config']['agent'] else workflow['config']['agent']['resources']
    callback_url = settings.API_URL + 'runs/' + task.guid + '/status/'
    work_dir = join(task.agent.workdir, task.workdir)
    new_flow = map_old_workflow_config_to_new(workflow, task, resources)  # TODO update flow UI page
    launcher = task.agent.launcher  # whether to use TACC launcher

    parse_errors, sub_options = parse_task_config(new_flow)
    if len(parse_errors) > 0:
        raise ValueError(f"Failed to parse task options: {' '.join(parse_errors)}")

    # create working directory
    execute_command(ssh_client=ssh, pre_command=':', command=f"mkdir {work_dir}", directory=task.agent.workdir, allow_stderr=True)

    # upload flow config and job script
    with ssh.client.open_sftp() as sftp:
        sftp.chdir(work_dir)

        # TODO refactor to allow multiple schedulers
        sandbox = task.agent.name == 'Sandbox'  # for now, we're either in the sandbox or on a SLURM cluster
        template = environ.get('CELERY_TEMPLATE_LOCAL_RUN_SCRIPT') if sandbox else environ.get('CELERY_TEMPLATE_SLURM_RUN_SCRIPT')
        template_name = template.split('/')[-1]

        # upload flow config file
        with sftp.open('flow.yaml', 'w') as flow_file:
            if launcher:
                del new_flow['jobqueue']
            yaml.dump(new_flow, flow_file, default_flow_style=False)

        # compose and upload job script
        with open(template, 'r') as template_script, sftp.open(template_name, 'w') as script:
            print(f"Uploading {template_name}")
            for line in template_script:
                script.write(line)

            if not sandbox:
                # we're on a SLURM cluster, so add resource requests
                nodes = min(len(input_files), task.agent.max_nodes) if input_files is not None and not task.agent.job_array else 1
                gpu = task.agent.gpu and ('gpu' in workflow['config'] and workflow['config']['gpu'])

                if 'cores' in resources:
                    cores = int(resources['cores'])
                    script.write(f"#SBATCH --cpus-per-task={cores}\n")
                if 'time' in resources:
                    split_time = resources['time'].split(':')
                    hours = int(split_time[0])
                    minutes = int(split_time[1])
                    seconds = int(split_time[2])
                    time = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                    # calculated [requested walltime * input files / nodes]
                    if input_files is not None:
                        adjusted_time = time * (len(input_files) / nodes)
                    else:
                        adjusted_time = time
                    hours = f"{min(ceil(adjusted_time.total_seconds() / 60 / 60), task.agent.max_nodes)}"
                    if len(hours) == 1:
                        hours = f"0{hours}"
                    adjusted_time_str = f"{hours}:00:00"

                    task.job_requested_walltime = adjusted_time_str
                    task.save()
                    msg = f"Using adjusted walltime {adjusted_time_str}"
                    log_task_status(task, msg)
                    push_task_event(task)
                    logger.info(msg)

                    script.write(f"#SBATCH --time={adjusted_time_str}\n")
                if 'mem' in resources and (task.agent.header_skip is None or '--mem' not in str(task.agent.header_skip)):
                    mem = resources['mem']
                    script.write(f"#SBATCH --mem={resources['mem']}\n")
                if task.agent.queue is not None and task.agent.queue != '':
                    queue = task.agent.gpu_queue if gpu else task.agent.queue
                    script.write(f"#SBATCH --partition={queue}\n")
                if task.agent.project is not None and task.agent.project != '':
                    script.write(f"#SBATCH -A {task.agent.project}\n")
                if gpu:
                    script.write(f"#SBATCH --gres=gpu:1\n")

                if input_files is not None and task.agent.job_array:
                    script.write(f"#SBATCH --array=1-{len(input_files)}\n")
                if input_files is not None:
                    script.write(f"#SBATCH -N {nodes}\n")
                    script.write(f"#SBATCH --ntasks={nodes}\n")
                else:
                    script.write(f"#SBATCH -N 1\n")
                    script.write("#SBATCH --ntasks=1\n")

                script.write("#SBATCH --mail-type=END,FAIL\n")
                script.write(f"#SBATCH --mail-user={task.user.email}\n")
                script.write("#SBATCH --output=plantit.%j.out\n")
                script.write("#SBATCH --error=plantit.%j.err\n")

            # add precommands
            script.write(task.agent.pre_commands + '\n')

            # pull singularity container in advance
            # script.write(f"singularity pull {run_options.image}\n")

            # if we have inputs, add pull command
            if 'input' in workflow['config']:
                input = workflow['config']['input']
                sftp.mkdir(join(task.agent.workdir, task.workdir, 'input'))

                # allow for both spellings of JPG
                patterns = [pattern.lower() for pattern in input['patterns']]
                if 'jpg' in patterns and 'jpeg' not in patterns:
                    patterns.append("jpeg")
                elif 'jpeg' in patterns and 'jpg' not in patterns:
                    patterns.append("jpg")

                pull_commands = f"plantit terrain pull \"{input['from']}\"" \
                                f" -p \"{join(task.agent.workdir, task.workdir, 'input')}\"" \
                                f" {' '.join(['--pattern ' + pattern for pattern in patterns])}" \
                                f""f" --terrain_token {task.user.profile.cyverse_access_token}"

                if task.agent.callbacks:
                    pull_commands += f""f" --plantit_url '{callback_url}' --plantit_token '{task.token}'"
                pull_commands += "\n"

                logger.info(f"Using pull command: {pull_commands}")
                script.write(pull_commands)

            docker_username = environ.get('DOCKER_USERNAME', None)
            docker_password = environ.get('DOCKER_PASSWORD', None)

            # if this resource uses TACC's launcher, create a parameter sweep script to invoke Singularity
            if launcher:
                logger.info(f"Using TACC launcher")
                with sftp.open('launch', 'w') as launcher_script:
                    if workflow['config']['input']['kind'] == 'files' and input_files is not None:
                        for file in input_files:
                            file_name = file.rpartition('/')[2]
                            sub_options.input = FileInput(file_name)
                            command = prep_command(
                                work_dir=sub_options.workdir,
                                image=sub_options.image,
                                command=sub_options.command,
                                parameters=(sub_options.parameters if sub_options.parameters is not None else []) + [
                                    Parameter(key='INPUT', value=join(task.agent.workdir, task.workdir, 'input', file_name))],
                                bind_mounts=sub_options.bind_mounts,
                                docker_username=docker_username,
                                docker_password=docker_password,
                                no_cache=sub_options.no_cache,
                                gpu=sub_options.gpu)
                            launcher_script.write(f"{command}\n")
                    elif workflow['config']['input']['kind'] == 'directory':
                        command = prep_command(
                            work_dir=sub_options.workdir,
                            image=sub_options.image,
                            command=sub_options.command,
                            parameters=(sub_options.parameters if sub_options.parameters is not None else []) + [
                                Parameter(key='INPUT', value=join(task.agent.workdir, task.workdir, 'input'))],
                            bind_mounts=sub_options.bind_mounts,
                            docker_username=docker_username,
                            docker_password=docker_password,
                            no_cache=sub_options.no_cache,
                            gpu=sub_options.gpu)
                        launcher_script.write(f"{command}\n")
                    elif workflow['config']['input']['kind'] == 'file':
                        command = prep_command(
                            work_dir=sub_options.workdir,
                            image=sub_options.image,
                            command=sub_options.command,
                            parameters=(sub_options.parameters if sub_options.parameters is not None else []) + [
                                Parameter(key='INPUT', value=new_flow['input']['file']['path'])],
                            bind_mounts=sub_options.bind_mounts,
                            docker_username=docker_username,
                            docker_password=docker_password,
                            no_cache=sub_options.no_cache,
                            gpu=sub_options.gpu)
                        launcher_script.write(f"{command}\n")

                script.write(f"export LAUNCHER_WORKDIR={join(task.agent.workdir, task.workdir)}\n")
                script.write(f"export LAUNCHER_JOB_FILE=launch\n")
                script.write("$LAUNCHER_DIR/paramrun\n")
            # otherwise use the CLI
            else:
                cli_cmd = f"plantit run flow.yaml"
                if task.agent.job_array and input_files is not None:
                    cli_cmd += f" --slurm_job_array"

                if docker_username is not None and docker_password is not None:
                    cli_cmd += f" --docker_username {docker_username} --docker_password {docker_password}"

                if task.agent.callbacks:
                    cli_cmd += f""f" --plantit_url '{callback_url}' --plantit_token '{task.token}'"

                cli_cmd += "\n"
                logger.info(f"Using CLI invocation: {cli_cmd}")
                script.write(cli_cmd)

            # add zip command
            output = workflow['config']['output']
            zip_commands = f"plantit zip {output['from'] if output['from'] != '' else '.'} -o . -n {task.guid}"
            log_files = [f"{task.guid}.{task.agent.name.lower()}.log"]
            zip_commands = f"{zip_commands} {' '.join(['--include_pattern ' + pattern for pattern in log_files])}"
            if 'include' in output:
                if 'patterns' in output['include']:
                    zip_commands = f"{zip_commands} {' '.join(['--include_pattern ' + pattern for pattern in output['include']['patterns']])}"
                if 'names' in output['include']:
                    zip_commands = f"{zip_commands} {' '.join(['--include_name ' + pattern for pattern in output['include']['names']])}"
                if 'patterns' in output['exclude']:
                    zip_commands = f"{zip_commands} {' '.join(['--exclude_pattern ' + pattern for pattern in output['exclude']['patterns']])}"
                if 'names' in output['exclude']:
                    zip_commands = f"{zip_commands} {' '.join(['--exclude_name ' + pattern for pattern in output['exclude']['names']])}"
            zip_commands += '\n'
            script.write(zip_commands)
            logger.info(f"Zipping enabled: {zip_commands}")

            # add push command if we have a destination
            # if 'to' in output and output['to'] is not None:
            #     push_commands = f"plantit terrain push {output['to']}" \
            #                     f" -p {join(run.work_dir, output['from'])}" \
            #                     f" --plantit_url '{callback_url}'"

            #     if 'include' in output:
            #         if 'patterns' in output['include']:
            #             push_commands = push_commands + ' '.join(
            #                 ['--include_pattern ' + pattern for pattern in output['include']['patterns']])
            #         if 'names' in output['include']:
            #             push_commands = push_commands + ' '.join(['--include_name ' + pattern for pattern in output['include']['names']])
            #         if 'patterns' in output['exclude']:
            #             push_commands = push_commands + ' '.join(
            #                 ['--exclude_pattern ' + pattern for pattern in output['exclude']['patterns']])
            #         if 'names' in output['exclude']:
            #             push_commands = push_commands + ' '.join(['--exclude_name ' + pattern for pattern in output['exclude']['names']])

            #     if run.resource.callbacks:
            #         push_commands += f""f" --plantit_url '{callback_url}' --plantit_token '{run.token}'"

            #     push_commands += '\n'
            #     script.write(push_commands)
            #     logger.info(f"Using push command: {push_commands}")


def submit_via_ssh(task: Task, ssh: SSH, file_count: int = None):
    # TODO refactor to allow multiple schedulers
    sandbox = task.agent.name == 'Sandbox'  # for now, we're either in the sandbox or on a SLURM cluster
    template = environ.get('CELERY_TEMPLATE_LOCAL_RUN_SCRIPT') if sandbox else environ.get('CELERY_TEMPLATE_SLURM_RUN_SCRIPT')
    template_name = template.split('/')[-1]

    if task.is_sandbox:
        execute_command(
            ssh_client=ssh,
            pre_command='; '.join(str(task.agent.pre_commands).splitlines()) if task.agent.pre_commands else ':',
            command=f"chmod +x {template_name} && ./{template_name}",
            directory=join(task.agent.workdir, task.workdir),
            allow_stderr=True)

        # get container logs
        work_dir = join(task.agent.workdir, task.workdir)
        container_log_file = get_container_log_file_name(task)
        container_log_path = get_container_log_file_path(task)

        with ssh.client.open_sftp() as sftp:
            cmd = 'test -e {0} && echo exists'.format(join(work_dir, container_log_file))
            stdin, stdout, stderr = ssh.client.exec_command(cmd)

            if not stdout.read().decode().strip() == 'exists':
                container_logs = []
            else:
                with open(get_container_log_file_path(task), 'a+') as log_file:
                    sftp.chdir(work_dir)
                    sftp.get(container_log_file, log_file.name)

                # obfuscate Docker auth info before returning logs to the user
                docker_username = environ.get('DOCKER_USERNAME', None)
                docker_password = environ.get('DOCKER_PASSWORD', None)
                for line in fileinput.input([container_log_path], inplace=True):
                    if docker_username in line.strip():
                        line = line.strip().replace(docker_username, '*' * 7, 1)
                    if docker_password in line.strip():
                        line = line.strip().replace(docker_password, '*' * 7)
                    sys.stdout.write(line)
    else:
        command = f"sbatch {template_name}"
        output_lines = execute_command(
            ssh_client=ssh,
            pre_command='; '.join(str(task.agent.pre_commands).splitlines()) if task.agent.pre_commands else ':',
            # if the scheduler prohibits nested job submissions, we need to run the CLI from a login node
            command=command,
            directory=join(task.agent.workdir, task.workdir),
            allow_stderr=True)
        job_id = parse_job_id(output_lines[-1])
        task.job_id = job_id
        task.updated = timezone.now()
        task.save()


def log_task_status(task: Task, description: str):
    log_path = join(environ.get('RUNS_LOGS'), f"{task.guid}.plantit.log")
    with open(log_path, 'a') as log:
        log.write(f"{description}\n")


async def push_task_event(task: Task):
    await get_channel_layer().group_send(f"runs-{task.user.username}", {
        'type': 'task_event',
        'run': map_task(task),
    })


def cancel_task(task: Task):
    ssh = SSH(task.agent.hostname, task.agent.port, task.agent.username)
    with ssh:
        lines = []
        for line in execute_command(
                ssh_client=ssh,
                pre_command=':',
                command=f"squeue -u {task.agent.username}",
                directory=join(task.agent.workdir, task.workdir)):
            logger.info(line)
            lines.append(line)

        if task.job_id is None or not any([task.job_id in r for r in lines]):
            return  # run doesn't exist, so no need to cancel

        execute_command(
            ssh_client=ssh,
            pre_command=':',
            command=f"scancel {task.job_id}",
            directory=join(task.agent.workdir, task.workdir))


def get_task_log_file_path(task: Task):
    return join(os.environ.get('RUNS_LOGS'), f"{task.guid}.plantit.log")


def get_container_log_file_name(task: Task):
    if task.agent.launcher:
        return f"plantit.{task.job_id}.out"
    else:
        return f"{task.guid}.{task.agent.name.lower()}.log"


def get_container_log_file_path(task: Task):
    return join(os.environ.get('RUNS_LOGS'), get_container_log_file_name(task))


def get_job_walltime(task: Task) -> (str, str):
    ssh = SSH(task.agent.hostname, task.agent.port, task.agent.username)
    with ssh:
        lines = execute_command(
            ssh_client=ssh,
            pre_command=":",
            command=f"squeue --user={task.agent.username}",
            directory=join(task.agent.workdir, task.workdir),
            allow_stderr=True)

        try:
            job_line = next(l for l in lines if task.job_id in l)
            job_split = job_line.split()
            job_walltime = job_split[-3]
            return job_walltime
        except StopIteration:
            return None


def get_job_status(task: Task) -> str:
    ssh = SSH(task.agent.hostname, task.agent.port, task.agent.username)
    with ssh:
        lines = execute_command(
            ssh_client=ssh,
            pre_command=':',
            command=f"sacct -j {task.job_id}",
            directory=join(task.agent.workdir, task.workdir),
            allow_stderr=True)

        job_line = next(l for l in lines if task.job_id in l)
        job_split = job_line.split()
        job_status = job_split[5].replace('+', '')
        return job_status
    pass


def get_result_files(task: Task, workflow: dict):
    included_by_name = ((workflow['output']['include']['names'] if 'names' in workflow['output'][
        'include'] else [])) if 'output' in workflow else []  # [f"{run.task_id}.zip"]
    included_by_name.append(f"{task.guid}.zip")  # zip file
    if not task.agent.launcher:
        included_by_name.append(f"{task.guid}.{task.agent.name.lower()}.log")
    if task.job_id is not None and task.job_id != '':
        included_by_name.append(f"plantit.{task.job_id}.out")
        included_by_name.append(f"plantit.{task.job_id}.err")
    included_by_pattern = (
        workflow['output']['include']['patterns'] if 'patterns' in workflow['output']['include'] else []) if 'output' in workflow else []

    client = SSH(task.agent.hostname, task.agent.port, task.agent.username)
    work_dir = join(task.agent.workdir, task.workdir)
    outputs = []
    seen = []

    with client:
        with client.client.open_sftp() as sftp:
            for file in included_by_name:
                file_path = join(work_dir, file)
                stdin, stdout, stderr = client.client.exec_command(f"test -e {file_path} && echo exists")
                output = {
                    'name': file,
                    'path': join(work_dir, file),
                    'exists': stdout.read().decode().strip() == 'exists'
                }
                seen.append(output['name'])
                outputs.append(output)

            for f in sftp.listdir(work_dir):
                if any(pattern in f for pattern in included_by_pattern):
                    if not any(s == f for s in seen):
                        outputs.append({
                            'name': f,
                            'path': join(work_dir, f),
                            'exists': True
                        })

    return outputs


def map_task(task: Task):
    task_log_file = get_task_log_file_path(task)

    if Path(task_log_file).is_file():
        with open(task_log_file, 'r') as log:
            task_logs = [line.strip() for line in log.readlines()[-int(1000000):]]
    else:
        task_logs = []

    try:
        AgentAccessPolicy.objects.get(user=task.user, agent=task.agent, role__in=[AgentRole.admin, AgentRole.guest])
        can_restart = True
    except:
        can_restart = False

    results = RedisClient.get().get(f"results/{task.guid}")

    t = {
        'can_restart': can_restart,
        'guid': task.guid,
        'status': task.status,
        'owner': task.user.username,
        'name': task.name,
        'work_dir': task.workdir,
        'task_logs': task_logs,
        'agent': task.agent.name,
        'created': task.created.isoformat(),
        'updated': task.updated.isoformat(),
        'completed': task.completed.isoformat() if task.completed is not None else None,
        'workflow_owner': task.workflow_owner,
        'workflow_name': task.workflow_name,
        'tags': [str(tag) for tag in task.tags.all()],
        'is_complete': task.is_complete,
        'is_success': task.is_success,
        'is_failure': task.is_failure,
        'is_cancelled': task.is_cancelled,
        'is_timeout': task.is_timeout,
        'workflow_image_url': task.workflow_image_url,
        'result_previews_loaded': task.previews_loaded,
        'cleaned_up': task.cleaned_up,
        'output_files': json.loads(results) if results is not None else []
    }

    if isinstance(task, JobQueueTask):
        t['job_id'] = task.job_id
        t['job_status'] = task.job_status
        t['job_walltime'] = task.job_elapsed_walltime

    return t


def map_delayed_task(task: DelayedTask):
    return {
        'agent': map_agent(task.agent),
        'name': task.name,
        'eta': task.eta,
        'interval': {
            'every': task.interval.every,
            'period': task.interval.period
        },
        'last_run': task.last_run_at
    }


def map_repeating_task(task: RepeatingTask):
    return {
        'agent': map_agent(task.agent),
        'name': task.name,
        'eta': task.eta,
        'interval': {
            'every': task.interval.every,
            'period': task.interval.period
        },
        'enabled': task.enabled,
        'last_run': task.last_run_at
    }
