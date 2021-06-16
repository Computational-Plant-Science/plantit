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
from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer
from dateutil import parser
from django.contrib.auth.models import User
from django.utils import timezone

from plantit import settings
from plantit import terrain
from plantit.agents.models import Agent, AgentAccessPolicy, AgentRole, AgentExecutor
from plantit.agents.utils import map_agent, has_virtual_memory
from plantit.docker import parse_image_components, image_exists
from plantit.redis import RedisClient
from plantit.ssh import SSH, execute_command
from plantit.tasks.models import Task, DelayedTask, RepeatingTask, TaskStatus, JobQueueTask
from plantit.tasks.options import PlantITCLIOptions, Parameter, Input, BindMount, PasswordTaskAuth, KeyTaskAuth, InputKind
from plantit.users.utils import get_private_key_path
from plantit.utils import parse_bind_mount, format_bind_mount

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


def parse_cli_options(task: Task) -> (List[str], PlantITCLIOptions):
    # update config before uploading
    config = task.workflow['config']
    config['workdir'] = join(task.agent.workdir, task.guid)
    config['log_file'] = f"{task.guid}.{task.agent.name.lower()}.log"
    if 'output' in config and 'from' in config['output']:
        if config['output']['from'] is not None and config['output']['from'] != '':
            config['output']['from'] = join(task.agent.workdir, task.workdir, config['output']['from'])

    # if we have outputs, make sure we don't push configuration or job scripts
    if 'output' in config:
        config['output']['exclude']['names'] = [
            f"{task.guid}.yaml",
            "template_local_run.sh",
            "template_slurm_run.sh"]

    jobqueue = None if 'jobqueue' not in config['agent'] else config['agent']['jobqueue']
    new_flow = map_workflow_config_to_cli_config(config, task, jobqueue)
    launcher = task.agent.launcher  # whether to use TACC launcher
    if task.agent.launcher: del new_flow['jobqueue']

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
    if not isinstance(config['commands'], str):
        errors.append('Attribute \'commands\' must not be a str')
    elif config['commands'] == '':
        errors.append('Attribute \'commands\' must not be empty')
    else:
        command = config['commands']

    parameters = None
    if 'parameters' in config:
        if not all(['name' in param and
                    param['name'] is not None and
                    param['name'] != '' and
                    'value' in param and
                    param['value'] is not None and
                    param['value'] != ''
                    for param in config['parameters']]):
            errors.append('Every parameter must have a non-empty \'name\' and \'value\'')
        else:
            parameters = [Parameter(key=param['name'], value=param['value']) for param in config['parameters']]

    bind_mounts = None
    if 'bind_mounts' in config:
        if not all(mount_point != '' for mount_point in config['bind_mounts']):
            errors.append('Every mount point must be non-empty')
        else:
            bind_mounts = [parse_bind_mount(work_dir, mount_point) for mount_point in config['bind_mounts']]

    input = None
    if 'input' in config:
        if 'kind' not in config['input']:
            errors.append("Section \'input\' must include attribute \'kind\'")
        if 'path' not in config['input']:
            errors.append("Section \'input\' must include attribute \'path\'")

        kind = config['input']['kind']
        path = config['input']['path']
        if kind == 'file':
            input = Input(path=path, kind='file')
        elif kind == 'files':
            input = Input(path=path, kind='files', patterns=config['input']['patterns'] if 'patterns' in config['input'] else None)
        elif kind == 'directory':
            input = Input(path=path, kind='directory')
        else:
            errors.append('Section \'input.kind\' must be \'file\', \'files\', or \'directory\'')

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

    return errors, PlantITCLIOptions(
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


def create_task(username: str, agent_name: str, workflow: dict, name: str = None, guid: str = None) -> Task:
    repo_owner = workflow['repo']['owner']['login']
    repo_name = workflow['repo']['name']
    agent = Agent.objects.get(name=agent_name)
    user = User.objects.get(username=username)
    if guid is None: guid = str(uuid.uuid4())  # if the browser client hasn't set a GUID, create one
    now = timezone.now()

    task = JobQueueTask.objects.create(
        guid=guid,
        name=name,
        user=user,
        workflow=workflow,
        workflow_owner=repo_owner,
        workflow_name=repo_name,
        agent=agent,
        status=TaskStatus.CREATED,
        created=now,
        updated=now,
        token=binascii.hexlify(
            os.urandom(
                20)).decode()) \
        if agent.executor != AgentExecutor.LOCAL else \
        Task.objects.create(
            guid=guid,
            name=guid if name is None else name,
            user=user,
            workflow=workflow,
            workflow_owner=repo_owner,
            workflow_name=repo_name,
            agent=agent,
            status=TaskStatus.CREATED,
            created=now,
            updated=now,
            token=binascii.hexlify(os.urandom(20)).decode())

    # add repo logo
    if 'logo' in workflow['config']:
        logo_path = workflow['config']['logo']
        task.workflow_image_url = f"https://raw.githubusercontent.com/{repo_name}/{repo_owner}/master/{logo_path}"

    for tag in workflow['config']['tags']: task.tags.add(tag)  # add task tags
    task.workdir = f"{task.guid}/"  # use GUID for working directory name
    task.save()
    return task


def configure_task_environment(task: Task, ssh: SSH):
    log_task_status(task, [f"Verifying configuration"])
    async_to_sync(push_task_event)(task)

    parse_errors, cli_options = parse_cli_options(task)
    if len(parse_errors) > 0: raise ValueError(f"Failed to parse task options: {' '.join(parse_errors)}")

    work_dir = join(task.agent.workdir, task.guid)
    log_task_status(task, [f"Creating working directory"])
    async_to_sync(push_task_event)(task)

    list(execute_command(ssh=ssh, precommand=':', command=f"mkdir {work_dir}"))

    log_task_status(task, [f"Uploading task executable"])
    async_to_sync(push_task_event)(task)

    upload_task_executables(task, ssh, cli_options)

    log_task_status(task, [f"Uploading task definition"])
    async_to_sync(push_task_event)(task)

    with ssh.client.open_sftp() as sftp:
        # TODO remove this utter hack
        if 'input' in cli_options:
            kind = cli_options['input']['kind']
            path = cli_options['input']['path']
            if kind == InputKind.DIRECTORY or kind == InputKind.FILES:
                cli_options['input']['path'] = 'input'
            else:
                cli_options['input']['path'] = f"input/{path.rpartition('/')[2]}"

        sftp.chdir(work_dir)
        with sftp.open(f"{task.guid}.yaml", 'w') as cli_file:
            yaml.dump(del_none(cli_options), cli_file, default_flow_style=False)
        if 'input' in cli_options: sftp.mkdir(join(work_dir, 'input'))


def compose_singularity_command(
        work_dir: str,
        image: str,
        command: str,
        bind_mounts: List[BindMount] = None,
        parameters: List[Parameter] = None,
        no_cache: bool = False,
        gpu: bool = False,
        docker_username: str = None,
        docker_password: str = None) -> str:
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
        print(f"Replacing '{parameter['key'].upper()}' with '{parameter['value']}'")
        command = command.replace(f"${parameter['key'].upper()}", parameter['value'])

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


def compose_resource_requests(task: Task, options: PlantITCLIOptions, inputs: List[str]) -> List[str]:
    nodes = min(len(inputs), task.agent.max_nodes) if inputs is not None and not task.agent.job_array else 1

    if ['jobqueue'] not in 'options': return []
    gpu = task.agent.gpu and ('gpu' in options and options['gpu'])
    jobqueue = options['jobqueue']
    commands = []

    if 'cores' in jobqueue: commands.append(f"#SBATCH --cpus-per-task={int(jobqueue['cores'])}\n")
    if 'memory' in jobqueue and not has_virtual_memory(task.agent): commands.append(f"#SBATCH --mem={jobqueue['mem']}\n")
    if 'walltime' in task.workflow['config']:
        split_time = task.workflow['config']['walltime'].split(':')
        hours = int(split_time[0])
        minutes = int(split_time[1])
        seconds = int(split_time[2])
        walltime = timedelta(hours=hours, minutes=minutes, seconds=seconds)

        # adjust walltime to compensate for inputs processed in parallel [requested walltime * input files / nodes]
        adjusted = walltime * (len(inputs) / nodes) if len(inputs) > 0 else walltime

        # round up to the nearest hour
        hours = f"{min(ceil(adjusted.total_seconds() / 60 / 60), task.agent.max_nodes)}"
        if len(hours) == 1: hours = f"0{hours}"
        adjusted_str = f"{hours}:00:00"

        log_task_status(task, [f"Using adjusted walltime {adjusted_str}"])
        async_to_sync(push_task_event)(task)

        task.job_requested_walltime = adjusted_str
        task.save()
        commands.append(f"#SBATCH --time={adjusted_str}\n")
    if gpu: commands.append(f"#SBATCH --gres=gpu:1\n")
    if task.agent.queue is not None and task.agent.queue != '': commands.append(
        f"#SBATCH --partition={task.agent.gpu_queue if gpu else task.agent.queue}\n")
    if task.agent.project is not None and task.agent.project != '': commands.append(f"#SBATCH -A {task.agent.project}\n")
    if len(inputs) > 0:
        if task.agent.job_array:
            commands.append(f"#SBATCH --array=1-{len(inputs)}\n")
        commands.append(f"#SBATCH -N {nodes}\n")
        commands.append(f"#SBATCH --ntasks={nodes}\n")
    else:
        commands.append(f"#SBATCH -N 1\n")
        commands.append("#SBATCH --ntasks=1\n")
    commands.append("#SBATCH --mail-type=END,FAIL\n")
    commands.append(f"#SBATCH --mail-user={task.user.email}\n")
    commands.append("#SBATCH --output=plantit.%j.out\n")
    commands.append("#SBATCH --error=plantit.%j.err\n")

    newline = '\n'
    logger.info(f"Using resource requests: {newline.join(commands)}")
    return commands


def compose_pull_command(task: Task, options: PlantITCLIOptions) -> str:
    if 'input' not in options: return ''
    input = options['input']
    if input is None: return ''
    kind = input['kind']

    if input['kind'] != InputKind.FILE and 'patterns' in input:
        # allow for both spellings of JPG
        patterns = [pattern.lower() for pattern in input['patterns']]
        if 'jpg' in patterns and 'jpeg' not in patterns: patterns.append("jpeg")
        elif 'jpeg' in patterns and 'jpg' not in patterns: patterns.append("jpg")
    else: patterns = []

    command = f"plantit terrain pull \"{input['path']}\"" \
              f" -p \"{join(task.agent.workdir, task.workdir, 'input')}\"" \
              f" {' '.join(['--pattern ' + pattern for pattern in patterns])}" \
              f""f" --terrain_token {task.user.profile.cyverse_access_token}"

    if task.agent.callbacks:
        callback_url = settings.API_URL + 'tasks/' + task.guid + '/status/'
        command += f""f" --plantit_url '{callback_url}' --plantit_token '{task.token}'"

    logger.info(f"Using pull command: {command}")
    return command


def compose_run_commands(task: Task, options: PlantITCLIOptions, inputs: List[str]) -> List[str]:
    docker_username = environ.get('DOCKER_USERNAME', None)
    docker_password = environ.get('DOCKER_PASSWORD', None)
    commands = []

    # if this resource uses TACC's launcher, create a parameter sweep script to invoke the Singularity container
    if task.agent.launcher:
        commands.append(f"export LAUNCHER_WORKDIR={join(task.agent.workdir, task.workdir)}\n")
        commands.append(f"export LAUNCHER_JOB_FILE={os.environ.get('LAUNCHER_SCRIPT_NAME')}\n")
        commands.append("$LAUNCHER_DIR/paramrun\n")
    # otherwise use the CLI
    else:
        command = f"plantit run {task.guid}.yaml"
        if task.agent.job_array and len(inputs) > 0:
            command += f" --slurm_job_array"

        if docker_username is not None and docker_password is not None:
            command += f" --docker_username {docker_username} --docker_password {docker_password}"

        if task.agent.callbacks:
            callback_url = settings.API_URL + 'tasks/' + task.guid + '/status/'
            command += f""f" --plantit_url '{callback_url}' --plantit_token '{task.token}'"

        commands.append(command)

    newline = '\n'
    logger.info(f"Using CLI commands: {newline.join(commands)}")
    return commands


def compose_zip_command(task: Task, options: PlantITCLIOptions) -> str:
    # if 'output' not in options: return ''
    output = options['output'] if 'output' in options else dict()
    # if output is None: return ''

    command = f"plantit zip {output['from'] if 'from' in output != '' else '.'} -o . -n {task.guid}"
    logs = [f"{task.guid}.{task.agent.name.lower()}.log"]
    command = f"{command} {' '.join(['--include_pattern ' + pattern for pattern in logs])}"

    if 'include' in output:
        if 'patterns' in output['include']:
            command = f"{command} {' '.join(['--include_pattern ' + pattern for pattern in output['include']['patterns']])}"
        if 'names' in output['include']:
            command = f"{command} {' '.join(['--include_name ' + pattern for pattern in output['include']['names']])}"
        if 'patterns' in output['exclude']:
            command = f"{command} {' '.join(['--exclude_pattern ' + pattern for pattern in output['exclude']['patterns']])}"
        if 'names' in output['exclude']:
            command = f"{command} {' '.join(['--exclude_name ' + pattern for pattern in output['exclude']['names']])}"

    logger.info(f"Using zip command: {command}")
    return command


def compose_push_command(options: PlantITCLIOptions) -> str:
    # TODO

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

    return ''


def compose_task_script(task: Task, options: PlantITCLIOptions, template: str) -> List[str]:
    with open(template, 'r') as template_file:
        template_header = [line for line in template_file]

    if 'input' in options and options['input'] is not None:
        kind = options['input']['kind']
        path = options['input']['path']
        if kind == InputKind.FILE:
            inputs = [terrain.get_file(path, task.user.profile.cyverse_access_token)]
        else:
            inputs = terrain.list_dir(path, task.user.profile.cyverse_access_token)
    else: inputs = []

    resource_requests = [] if task.agent.executor == AgentExecutor.LOCAL else compose_resource_requests(task, options, inputs)
    pre_commands = task.agent.pre_commands
    pull_command = compose_pull_command(task, options)
    run_commands = compose_run_commands(task, options, inputs)
    zip_command = compose_zip_command(task, options)
    push_command = compose_push_command(options)

    return template_header + resource_requests + [pre_commands] + [pull_command] + run_commands + [zip_command] + [push_command]


def compose_launcher_script(task: Task, options: PlantITCLIOptions) -> List[str]:
    docker_username = environ.get('DOCKER_USERNAME', None)
    docker_password = environ.get('DOCKER_PASSWORD', None)
    lines = []

    if 'input' in options:
        if options['input']['kind'] == 'files':
            files = list_input_files(task, options) if ('input' in options and options['input']['kind'] == 'files') else []
            for file in files:
                file_name = file.rpartition('/')[2]
                command = compose_singularity_command(
                    work_dir=options['workdir'],
                    image=options['image'],
                    command=options['command'],
                    parameters=(options['parameters'] if 'parameters' in options else []) + [
                        Parameter(key='INPUT', value=join(options['workdir'], 'input', file_name))],
                    bind_mounts=options['bind_mounts'],
                    no_cache=options['no_cache'],
                    gpu=options['gpu'],
                    docker_username=docker_username,
                    docker_password=docker_password)
                lines.append(command)
        elif options['input']['kind'] == 'directory':
            command = compose_singularity_command(
                work_dir=options['workdir'],
                image=options['image'],
                command=options['command'],
                parameters=(options['parameters'] if 'parameters' in options else []) + [
                    Parameter(key='INPUT', value=join(options['workdir'], 'input'))],
                bind_mounts=options['bind_mounts'],
                no_cache=options['no_cache'],
                gpu=options['gpu'],
                docker_username=docker_username,
                docker_password=docker_password)
            lines.append(command)
        elif options['input']['kind'] == 'file':
            file_name = options['input']['path'].rpartition('/')[2]
            command = compose_singularity_command(
                work_dir=options['workdir'],
                image=options['image'],
                command=options['command'],
                parameters=(options['parameters'] if 'parameters' in options else []) + [
                    Parameter(key='INPUT', value=join(options['workdir'], file_name))],
                bind_mounts=options['bind_mounts'],
                no_cache=options['no_cache'],
                gpu=options['gpu'],
                docker_username=docker_username,
                docker_password=docker_password)
            lines.append(command)
    else:
        command = compose_singularity_command(
            work_dir=options['workdir'],
            image=options['image'],
            command=options['command'],
            parameters=(options['parameters'] if 'parameters' in options else []),
            bind_mounts=options['bind_mounts'],
            no_cache=options['no_cache'],
            gpu=options['gpu'],
            docker_username=docker_username,
            docker_password=docker_password)
        lines.append(command)

    return lines


def upload_task_executables(task: Task, ssh: SSH, options: PlantITCLIOptions):
    with ssh.client.open_sftp() as sftp:
        workdir = join(task.agent.workdir, task.workdir)
        sftp.chdir(workdir)
        template_path = environ.get('CELERY_TEMPLATE_LOCAL_RUN_SCRIPT') if task.agent.executor == AgentExecutor.LOCAL else environ.get(
            'CELERY_TEMPLATE_SLURM_RUN_SCRIPT')
        with sftp.open(f"{task.guid}.sh", 'w') as task_script:
            task_commands = compose_task_script(task, options, template_path)
            for line in task_commands:
                if line != '': task_script.write(line + "\n")

        # if the selected agent uses the Launcher, create a parameter sweep script too
        if task.agent.launcher:
            with sftp.open(os.environ.get('LAUNCHER_SCRIPT_NAME'), 'w') as launcher_script:
                launcher_commands = compose_launcher_script(task, options)
                for line in launcher_commands:
                    if line != '': launcher_script.write(line + "\n")


def execute_local_task(task: Task, ssh: SSH):
    precommand = '; '.join(str(task.agent.pre_commands).splitlines()) if task.agent.pre_commands else ':'
    command = f"chmod +x {task.guid}.sh && ./{task.guid}.sh"
    workdir = join(task.agent.workdir, task.workdir)

    count = 0
    lines = []
    for line in execute_command(ssh=ssh, precommand=precommand, command=command, directory=workdir, allow_stderr=True):
        stripped = line.strip()
        if count < 4 and stripped:  # TODO make the chunking size configurable
            lines.append(stripped)
            count += 1
        else:
            log_task_status(task, [f"[{task.agent.name}] {line}" for line in lines])
            lines = []
            count = 0

    task.status = TaskStatus.SUCCESS
    now = timezone.now()
    task.updated = now
    task.completed = now
    task.save()


def submit_jobqueue_task(task: Task, ssh: SSH) -> str:
    precommand = '; '.join(str(task.agent.pre_commands).splitlines()) if task.agent.pre_commands else ':'
    command = f"sbatch {task.guid}.sh"
    workdir = join(task.agent.workdir, task.workdir)
    output_lines = execute_command(ssh=ssh, precommand=precommand, command=command, directory=workdir, allow_stderr=True)

    job_id = parse_job_id(output_lines[-1])
    task.job_id = job_id
    task.updated = timezone.now()
    task.save()

    return job_id


def log_task_status(task: Task, messages: List[str]):
    log_path = join(environ.get('RUNS_LOGS'), f"{task.guid}.plantit.log")
    with open(log_path, 'a') as log:
        for message in messages:
            logger.info(f"[Task {task.guid} ({task.user.username}/{task.name})] {message}")
            log.write(f"{message}\n")


@sync_to_async
def get_task_user(task: Task):
    return task.user


async def push_task_event(task: Task):
    user = await get_task_user(task)
    await get_channel_layer().group_send(f"tasks-{user.username}", {
        'type': 'task_event',
        'task': await sync_to_async(map_task)(task),
    })


def cancel_task(task: Task):
    ssh = SSH(task.agent.hostname, task.agent.port, task.agent.username)
    with ssh:
        if isinstance(task, JobQueueTask):
            lines = []
            for line in execute_command(
                    ssh=ssh,
                    precommand=':',
                    command=f"squeue -u {task.agent.username}",
                    directory=join(task.agent.workdir, task.workdir)):
                logger.info(line)
                lines.append(line)

            if task.job_id is None or not any([task.job_id in r for r in lines]):
                return  # run doesn't exist, so no need to cancel

            execute_command(
                ssh=ssh,
                precommand=':',
                command=f"scancel {task.job_id}",
                directory=join(task.agent.workdir, task.workdir))


def get_task_log_file_path(task: Task):
    return join(os.environ.get('RUNS_LOGS'), f"{task.guid}.plantit.log")


def get_container_log_file_name(task: Task):
    if isinstance(task, JobQueueTask) and task.agent.launcher:
        return f"plantit.{task.job_id}.out"
    else:
        return f"{task.guid}.{task.agent.name.lower()}.log"


def get_container_log_file_path(task: Task):
    return join(os.environ.get('RUNS_LOGS'), get_container_log_file_name(task))


def get_container_logs(task: Task, ssh: SSH):
    work_dir = join(task.agent.workdir, task.workdir)
    container_log_file = get_container_log_file_name(task)
    container_log_path = get_container_log_file_path(task)

    with ssh:
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


def get_job_walltime(task: JobQueueTask) -> (str, str):
    ssh = SSH(task.agent.hostname, task.agent.port, task.agent.username)
    with ssh:
        lines = execute_command(
            ssh=ssh,
            precommand=":",
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


def get_job_status(task: JobQueueTask) -> str:
    ssh = SSH(task.agent.hostname, task.agent.port, task.agent.username)
    with ssh:
        lines = execute_command(
            ssh=ssh,
            precommand=':',
            command=f"sacct -j {task.job_id}",
            directory=join(task.agent.workdir, task.workdir),
            allow_stderr=True)

        job_line = next(l for l in lines if task.job_id in l)
        job_split = job_line.split()
        job_status = job_split[5].replace('+', '')
        return job_status
    pass


def get_result_files(task: Task, workflow: dict, auth: dict):
    included_by_name = ((workflow['output']['include']['names'] if 'names' in workflow['output'][
        'include'] else [])) if 'output' in workflow else []  # [f"{run.task_id}.zip"]
    included_by_name.append(f"{task.guid}.zip")  # zip file
    if not task.agent.launcher:
        included_by_name.append(f"{task.guid}.{task.agent.name.lower()}.log")
    if isinstance(task, JobQueueTask) and task.job_id is not None and task.job_id != '':
        included_by_name.append(f"plantit.{task.job_id}.out")
        included_by_name.append(f"plantit.{task.job_id}.err")
    included_by_pattern = (
        workflow['output']['include']['patterns'] if 'patterns' in workflow['output']['include'] else []) if 'output' in workflow else []

    ssh = get_ssh_client(task, auth)
    workdir = join(task.agent.workdir, task.workdir)
    outputs = []
    seen = []

    with ssh:
        with ssh.client.open_sftp() as sftp:
            for file in included_by_name:
                file_path = join(workdir, file)
                stdin, stdout, stderr = ssh.client.exec_command(f"test -e {file_path} && echo exists")
                output = {
                    'name': file,
                    'path': join(workdir, file),
                    'exists': stdout.read().decode().strip() == 'exists'
                }
                seen.append(output['name'])
                outputs.append(output)

            for f in sftp.listdir(workdir):
                if any(pattern in f for pattern in included_by_pattern):
                    if not any(s == f for s in seen):
                        outputs.append({
                            'name': f,
                            'path': join(workdir, f),
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


def list_input_files(task: Task, options: PlantITCLIOptions) -> List[str]:
    input_files = terrain.list_dir(options['input']['path'], task.user.profile.cyverse_access_token)
    msg = f"Found {len(input_files)} input file(s)"
    log_task_status(task, msg)
    async_to_sync(push_task_event)(task)
    logger.info(msg)

    return input_files


def get_ssh_client(task: Task, auth: dict) -> SSH:
    username = auth['username']
    if 'password' in auth:
        logger.info(f"Using password authentication (username: {username})")
        client = SSH(host=task.agent.hostname, port=task.agent.port, username=username, password=auth['password'])
    elif 'path' in auth:
        logger.info(f"Using key authentication (username: {username})")
        client = SSH(host=task.agent.hostname, port=task.agent.port, username=task.agent.username, pkey=auth['path'])
    else: raise ValueError(f"Unrecognized authentication strategy")

    return client


def map_workflow_config_to_cli_config(config: dict, task: Task, resources: dict) -> dict:
    cli_config = {
        'image': config['image'],
        'command': config['commands'],
        'workdir': config['workdir'],
        'log_file': f"{task.guid}.{task.agent.name.lower()}.log"
    }

    del config['agent']

    if 'mount' in config:
        cli_config['bind_mounts'] = config['mount']

    if 'parameters' in config:
        old_params = config['parameters']
        params = []
        for p in old_params:
            if p['type'] == 'string':
                params.append({
                    'key': p['name'],
                    'value': str(p['value'])
                })
            elif p['type'] == 'select':
                params.append({
                    'key': p['name'],
                    'value': str(p['value'])
                })
            elif p['type'] == 'number':
                params.append({
                    'key': p['name'],
                    'value': str(p['value'])
                })
            elif p['type'] == 'boolean':
                params.append({
                    'key': p['name'],
                    'value': str(p['value'])
                })
        cli_config['parameters'] = params

    if 'input' in config:
        input_kind = config['input']['kind'] if 'kind' in config['input'] else None
        cli_config['input'] = dict()
        if input_kind == 'directory':
            cli_config['input']['directory'] = dict()
            cli_config['input']['directory']['path'] = join(task.agent.workdir, task.workdir, 'input')
            cli_config['input']['directory']['patterns'] = config['input']['patterns']
        elif input_kind == 'files':
            cli_config['input']['files'] = dict()
            cli_config['input']['files']['path'] = join(task.agent.workdir, task.workdir, 'input')
            cli_config['input']['files']['patterns'] = config['input']['patterns']
        elif input_kind == 'file':
            cli_config['input']['file'] = dict()
            cli_config['input']['file']['path'] = join(task.agent.workdir, task.workdir, 'input',
                                                       config['input']['from'].rpartition('/')[2])

    sandbox = task.agent.name == 'Sandbox'
    work_dir = join(task.agent.workdir, task.workdir)
    if not sandbox and not task.agent.job_array:
        cli_config['jobqueue'] = dict()
        cli_config['jobqueue']['slurm'] = {
            'cores': resources['cores'],
            'processes': resources['processes'],
            'walltime': resources['time'],
            'local_directory': work_dir,
            'log_directory': work_dir,
            'env_extra': [task.agent.pre_commands]
        }

        if 'mem' in resources:
            cli_config['jobqueue']['slurm']['memory'] = resources['mem']
        if task.agent.queue is not None and task.agent.queue != '':
            cli_config['jobqueue']['slurm']['queue'] = task.agent.queue
        if task.agent.project is not None and task.agent.project != '':
            cli_config['jobqueue']['slurm']['project'] = task.agent.project
        if task.agent.header_skip is not None and task.agent.header_skip != '':
            cli_config['jobqueue']['slurm']['header_skip'] = task.agent.header_skip.split(',')

        if 'gpu' in config and config['gpu']:
            if task.agent.gpu:
                print(f"Using GPU on {task.agent.name} queue '{task.agent.gpu_queue}'")
                cli_config['gpu'] = True
                cli_config['jobqueue']['slurm']['job_extra'] = [f"--gres=gpu:1"]
                cli_config['jobqueue']['slurm']['queue'] = task.agent.gpu_queue
            else:
                print(f"No GPU support on {task.agent.name}")

    return cli_config


def del_none(d) -> dict:
    """
    Delete keys with the value ``None`` in a dictionary, recursively.

    This alters the input so you may wish to ``copy`` the dict first.

    Referenced from https://stackoverflow.com/a/4256027.
    """
    # For Python 3, write `list(d.items())`; `d.items()` won’t work
    # For Python 2, write `d.items()`; `d.iteritems()` won’t work
    for key, value in list(d.items()):
        if value is None:
            del d[key]
        elif isinstance(value, dict):
            del_none(value)
    return d  # For convenience


def parse_auth_options(auth: dict) -> dict:
    if 'password' in auth: return PasswordTaskAuth(username=auth['username'], password=auth['password'])
    else: return KeyTaskAuth(username=auth['username'], path=str(get_private_key_path(auth['username'])))
