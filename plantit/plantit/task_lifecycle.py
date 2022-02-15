import os
import subprocess
import tempfile
import logging
import traceback
from os import environ
from os.path import join, isdir
from pathlib import Path
from typing import List, Tuple

import binascii
import json
import uuid
from datetime import timedelta

import yaml
from asgiref.sync import async_to_sync

from django.contrib.auth.models import User
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTasks

from paramiko.ssh_exception import AuthenticationException, ChannelException, NoValidConnectionsError, SSHException
from tenacity import retry, wait_random_exponential, stop_after_attempt, retry_if_exception_type

from plantit import docker as docker
from plantit.agents.models import Agent, AgentScheduler
from plantit.miappe.models import Investigation, Study
from plantit.redis import RedisClient
from plantit.ssh import SSH, execute_command
from plantit.task_resources import get_task_ssh_client, push_task_channel_event, log_task_orchestrator_status
from plantit.task_scripts import compose_task_run_script, compose_task_launcher_script
from plantit.tasks.models import DelayedTask, RepeatingTask, Task, TaskStatus, TaskCounter, TaskOptions, InputKind, \
    EnvironmentVariable, Parameter, \
    Input
from plantit.utils.misc import del_none
from plantit.utils.tasks import parse_task_eta, parse_task_time_limit, parse_task_job_id, get_output_included_names, get_output_included_patterns, \
    get_task_scheduler_log_file_path, get_task_scheduler_log_file_name, parse_bind_mount, parse_task_miappe_info
from plantit.keypairs import get_user_private_key_path

logger = logging.getLogger(__name__)


def create_immediate_task(user: User, config: dict):
    # set submission time so we can persist configuration
    # and show recent submissions to the user in the UI
    config['timestamp'] = timezone.now().isoformat()

    # parse GitHub repo info
    repo_owner = config['repo']['owner']
    repo_name = config['repo']['name']
    repo_branch = config['repo']['branch']

    # persist task configuration
    redis = RedisClient.get()
    redis.set(f"workflow_configs/{user.username}/{repo_owner}/{repo_name}/{repo_branch}", json.dumps(config))

    # get the task GUID and name
    guid = config.get('guid', None) if config['type'] == 'Now' else str(uuid.uuid4())
    name = config.get('name', None)

    # if the browser client hasn't set a GUID, create one
    if guid is None: guid = str(uuid.uuid4())

    # get the agent this task should be submitted on
    agent = Agent.objects.get(name=config['agent'])

    # if we have a time limit, calculate due time
    time = config.get('time', None)
    if time is not None:
        time_limit = parse_task_time_limit(time)
        logger.info(f"Using task time limit {time_limit}s")
        due_time = timezone.now() + timedelta(seconds=time_limit)
    else: due_time = None

    # create the task right meow
    now = timezone.now()
    task = Task.objects.create(
        guid=guid,
        name=guid if name is None or name == '' else name,
        user=user,
        workflow=config['workflow'],
        workflow_owner=repo_owner,
        workflow_name=repo_name,
        workflow_branch=repo_branch,
        agent=agent,
        status=TaskStatus.CREATED,
        created=now,
        updated=now,
        due_time=due_time,
        token=binascii.hexlify(os.urandom(20)).decode())

    # add MIAPPE info, if we have any
    project, study = parse_task_miappe_info(config['miappe'])
    if project is not None: task.project = Investigation.objects.get(owner=user, title=project)
    if study is not None: task.study = Study.objects.get(investigation=task.project, title=study)

    # add repo logo
    if 'logo' in config['workflow']:
        logo_path = config['workflow']['logo']
        task.workflow_image_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/master/{logo_path}"

    for tag in config['tags']: task.tags.add(tag)  # add task tags
    task.workdir = f"{task.guid}/"  # use GUID for working directory name
    task.save()

    # increment task count for aggregate statistics
    counter = TaskCounter.load()
    counter.count = counter.count + 1
    counter.save()

    return task


def create_delayed_task(user: User, config: dict):
    now = timezone.now().timestamp()
    id = f"{user.username}-delayed-{now}"
    eta, seconds = parse_task_eta(config['eta'])
    schedule, _ = IntervalSchedule.objects.get_or_create(every=seconds, period=IntervalSchedule.SECONDS)

    # parse GitHub repo info
    repo_owner = config['repo']['owner']
    repo_name = config['repo']['name']
    repo_branch = config['repo']['branch']

    if 'logo' in config:
        logo_path = config['logo']
        workflow_image_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{repo_branch}/{logo_path}"
    else:
        workflow_image_url = None

    task, created = DelayedTask.objects.get_or_create(
        user=user,
        interval=schedule,
        eta=eta,
        one_off=True,
        workflow_owner=repo_owner,
        workflow_name=repo_name,
        workflow_branch=repo_branch,
        workflow_image_url=workflow_image_url,
        name=id,
        task='plantit.celery_tasks.create_and_submit_delayed',
        args=json.dumps([user.username, config, id]))

    # manually refresh task schedule
    PeriodicTasks.changed(task)

    return task, created


def create_repeating_task(user: User, workflow):
    now = timezone.now().timestamp()
    id = f"{user.username}-repeating-{now}"
    eta, seconds = parse_task_eta(workflow['eta'])
    schedule, _ = IntervalSchedule.objects.get_or_create(every=seconds, period=IntervalSchedule.SECONDS)

    repo_owner = workflow['repo']['owner']
    repo_name = workflow['repo']['name']
    repo_branch = workflow['repo']['branch']

    if 'logo' in workflow:
        logo_path = workflow['logo']
        workflow_image_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/{repo_branch}/{logo_path}"
    else:
        workflow_image_url = None

    task, created = RepeatingTask.objects.get_or_create(
        user=user,
        interval=schedule,
        eta=eta,
        workflow_owner=repo_owner,
        workflow_name=repo_name,
        workflow_branch=repo_branch,
        workflow_image_url=workflow_image_url,
        name=id,
        task='plantit.celery_tasks.create_and_submit_repeating',
        args=json.dumps([user.username, workflow, id]))

    # manually refresh task schedule
    PeriodicTasks.changed(task)

    return task, created


def upload_deployment_artifacts(task: Task, ssh: SSH, options: TaskOptions):
    # working directory
    work_dir = join(task.agent.workdir, task.workdir)

    # NOTE: paramiko is finicky about connecting to certain hosts.
    # the equivalent paramiko implementation is commented below,
    # but for now we just perform each step manually.
    #
    # issues #239: https://github.com/Computational-Plant-Science/plantit/issues/239
    #
    # misc:
    # - if sftp throws an IOError or complains about filesizes,
    #   it probably means the remote host's disk is full.
    #   could catch the error and show an alert in the UI.

    # if this workflow has input files, create a directory for them
    if 'input' in options:
        logger.info(f"Creating input directory for task {task.guid}")
        list(execute_command(ssh=ssh, precommand=':', command=f"mkdir {join(work_dir, 'input')}"))

    # compose the task script, write a temporary local copy, then transfer it to the deployment target
    with tempfile.NamedTemporaryFile() as task_script:
        lines = compose_task_run_script(task, options, environ.get('TASKS_TEMPLATE_SCRIPT_SLURM'))
        for line in lines: task_script.write(f"{line}\n".encode('utf-8'))
        task_script.seek(0)
        logger.info(os.stat(task_script.name))
        cmd = f"scp -v -o StrictHostKeyChecking=no -i {str(get_user_private_key_path(task.agent.user.username))} {task_script.name} {task.agent.username}@{task.agent.hostname}:{join(work_dir, task.guid)}.sh"
        logger.info(f"Uploading job script for task {task.guid} using command: {cmd}")
        subprocess.run(cmd, shell=True)

    # if the selected agent uses the TACC Launcher, create and upload a launcher script too
    if task.agent.launcher:
        with tempfile.NamedTemporaryFile() as launcher_script:
            launcher_commands = compose_task_launcher_script(task, options)
            for line in launcher_commands: launcher_script.write(f"{line}\n".encode('utf-8'))
            launcher_script.seek(0)
            logger.info(os.stat(launcher_script.name))
            cmd = f"scp -v -o StrictHostKeyChecking=no -i {str(get_user_private_key_path(task.agent.user.username))} {launcher_script.name} {task.agent.username}@{task.agent.hostname}:{join(work_dir, os.environ.get('LAUNCHER_SCRIPT_NAME'))}"
            logger.info(f"Uploading launcher script for task {task.guid} using command: {cmd}")
            subprocess.run(cmd, shell=True)
    else:
        # TODO upload list of input files for SLURM job arrays
        pass


def submit_task_to_scheduler(task: Task, ssh: SSH) -> str:
    precommand = '; '.join(str(task.agent.pre_commands).splitlines()) if task.agent.pre_commands else ':'
    command = f"sbatch {task.guid}.sh"
    workdir = join(task.agent.workdir, task.workdir)

    lines = []
    for line in execute_command(ssh=ssh, precommand=precommand, command=command, directory=workdir, allow_stderr=True):
        stripped = line.strip()
        if stripped:
            logger.info(f"[{task.agent.name}] {stripped}")
            # log_task_orchestrator_status(task, [f"[{task.agent.name}] {stripped}"])
            lines.append(stripped)

    job_id = parse_task_job_id(lines[-1])
    task.job_id = job_id
    task.updated = timezone.now()
    task.save()

    logger.info(f"Set task {task.guid} job ID: {task.job_id}")
    return job_id


def cancel_task(task: Task):
    ssh = get_task_ssh_client(task)
    with ssh:
        lines = []
        try:
            for line in execute_command(
                    ssh=ssh,
                    precommand=':',
                    command=f"squeue -u {task.agent.username}",
                    directory=join(task.agent.workdir, task.workdir),
                    allow_stderr=True):
                logger.info(line)
                lines.append(line)

            if task.job_id is None and not any([task.job_id in r for r in lines]):
                return  # run doesn't exist, so no need to cancel
        except:
            logger.warning(f"Error canceling job on {task.agent.name}: {traceback.format_exc()}")
            return

        # TODO support PBS/other scheduler cancellation commands, not just SLURM
        if task.job_id is not None:
            try:
                execute_command(
                    ssh=ssh,
                    precommand=':',
                    command=f"scancel {task.job_id}",
                    directory=join(task.agent.workdir, task.workdir))
            except:
                logger.warning(f"Error canceling job on {task.agent.name}: {traceback.format_exc()}")


def check_job_logs_for_progress(task: Task):
    """
    Parse scheduler log files for CLI output and update progress counters

    Args:
        task: The task
    """

    scheduler_log_file_path = get_task_scheduler_log_file_path(task)
    if not Path(scheduler_log_file_path).is_file():
        logger.warning(f"Scheduler log file {get_task_scheduler_log_file_name(task)} does not exist yet")
        return

    with open(scheduler_log_file_path, 'r') as scheduler_log_file:
        lines = scheduler_log_file.readlines()
        all_lines = '\n'.join(lines)

        task.inputs_downloaded = all_lines.count('Downloading file')
        task.results_transferred = all_lines.count('Uploading file')

        if task.agent.launcher:
            task.inputs_submitted = all_lines.count('running job')
            task.inputs_completed = all_lines.count('done. Exiting')
        else:
            task.inputs_submitted = all_lines.count('Submitting container')
            task.inputs_completed = all_lines.count('Container completed')

        task.save()


@retry(
    wait=wait_random_exponential(multiplier=5, max=120),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(AuthenticationException) | retry_if_exception_type(AuthenticationException) | retry_if_exception_type(ChannelException) | retry_if_exception_type(NoValidConnectionsError) | retry_if_exception_type(SSHException)),
    reraise=True)
def get_job_status_and_walltime(task: Task):
    ssh = get_task_ssh_client(task)
    status = None
    walltime = None

    with ssh:
        # first get the job's walltime
        lines = execute_command(
            ssh=ssh,
            precommand=":",
            command=f"squeue --user={task.agent.username}",
            directory=join(task.agent.workdir, task.workdir),
            allow_stderr=True)

        try:
            job_line = next(l for l in lines if task.job_id in l)
            job_split = job_line.split()
            walltime = job_split[-3]
        except StopIteration:
            # if we don't receive any lines of output, the job wasn't found
            pass

        # next get the job's status
        lines = execute_command(
            ssh=ssh,
            precommand=':',
            command=f"sacct -j {task.job_id}",
            directory=join(task.agent.workdir, task.workdir),
            allow_stderr=True)

        try:
            line = next(l for l in lines if task.job_id in l)
            status = line.split()[5].replace('+', '')
            return status, walltime
        except StopIteration:
            # if we don't receive any lines of output, the job wasn't found
            pass

        # check the scheduler log file in case `sacct` is no longer displaying info
        # about this job so we don't miss a cancellation/timeout/failure/completion
        with ssh.client.open_sftp() as sftp:

            log_file_path = get_task_scheduler_log_file_path(task)
            stdin, stdout, stderr = ssh.client.exec_command(f"test -e {log_file_path} && echo exists")

            # if log file doesn't exist, return None
            if stdout.read().decode().strip() != 'exists': status = None

            # otherwise check the log file to see if job status was written there
            else:
                with sftp.open(log_file_path, 'r') as log_file:
                    logger.info(f"Checking scheduler log file {log_file_path} for job {task.job_id} status")

                    for line in log_file.readlines():
                        # if we find success or failure, stop
                        if 'FAILED' in line or 'FAILURE' in line or 'NODE_FAIL' in line:
                            status = 'FAILED'
                            break
                        if 'SUCCESS' in line or 'COMPLETED' in line:
                            status = 'SUCCESS'
                            break

                        # otherwise use the most recent status (last line of the log file)
                        if 'CANCELLED' in line or 'CANCELED' in line:
                            status = 'CANCELED'
                            continue
                        if 'TIMEOUT' in line:
                            status = 'TIMEOUT'
                            continue

    return status, walltime


def list_result_files(task: Task) -> List[dict]:
    """
    Lists result files expected to be produced by the given task (assumes the task has completed). Returns a dict with form `{'name': <name>, 'path': <full path>, 'exists': <True or False>}`

    Args:
        task: The task

    Returns: Result files expected to be produced by the task

    """

    seen = []
    results = []
    ssh = get_task_ssh_client(task)
    workdir = join(task.agent.workdir, task.workdir)
    expected_names = get_output_included_names(task)
    expected_patterns = get_output_included_patterns(task)

    with ssh:
        with ssh.client.open_sftp() as sftp:
            # list contents of task working directory
            names = sftp.listdir(workdir)

            # check for files by name
            logger.info(f"Looking for files by name: {', '.join(expected_patterns)}")
            for name in expected_names:
                if name in names:
                    exists = True
                    seen.append(name)
                else:
                    exists = False

                output = {
                    'name': name,
                    'path': join(workdir, name),
                    'exists': exists
                }
                results.append(output)


                # file_path = join(workdir, expected_name)
                # stdin, stdout, stderr = ssh.client.exec_command(f"test -e {file_path} && echo exists")
                # output = {
                #     'name': expected_name,
                #     'path': join(workdir, expected_name),
                #     'exists': stdout.read().decode().strip() == 'exists'
                # }
                # seen.append(output['name'])
                # outputs.append(output)

            # check for files by pattern, excluding any we've already matched by name
            logger.info(f"Looking for files by pattern: {', '.join(expected_patterns)}")
            for pattern in expected_patterns:

                # check if the pattern matches any of the directory contents
                any_matched = False
                for name in names:
                    # if this filename matches a pattern and hasn't already been included by name, add it to the list
                    if pattern in name:
                        if not any(s == name for s in seen):
                            results.append({
                                'name': name,
                                'path': join(workdir, name),
                                'exists': True
                            })

                        # if the pattern matched something already included by name, don't count it as missing
                        any_matched = True

                # otherwise report the pattern missing
                if not any_matched:
                    results.append({
                        'name': f"*.{pattern}",
                        'path': join(workdir, f"*.{pattern}"),
                        'exists': False
                    })

    logger.info(f"Expecting {len(results)}+ result files for task {task.guid}: {', '.join([o['name'] for o in results])}")
    return results


def parse_task_options(task: Task) -> (List[str], TaskOptions):
    config = task.workflow
    config['workdir'] = join(task.agent.workdir, task.guid)
    config['log_file'] = f"{task.guid}.{task.agent.name.lower()}.log"

    # set the output directory (if none is set, use the task working dir)
    default_from = join(task.agent.workdir, task.workdir)
    if 'output' in config:
        if 'from' in config['output']:
            if config['output']['from'] is not None and config['output']['from'] != '':
                config['output']['from'] = join(task.agent.workdir, task.workdir, config['output']['from'])
            else:
                config['output']['from'] = default_from
        else:
            config['output']['from'] = default_from
    else:
        config['output'] = dict()
        config['output']['from'] = default_from

    if 'include' not in config['output']: config['output']['include'] = dict()
    if 'patterns' not in config['output']['include']: config['output']['exclude']['patterns'] = []

    # include scheduler logs
    config['output']['include']['patterns'].append("out")
    config['output']['include']['patterns'].append("err")
    config['output']['include']['patterns'].append("log")

    if 'exclude' not in config['output']: config['output']['exclude'] = dict()
    if 'names' not in config['output']['exclude']: config['output']['exclude']['names'] = []

    # exclude template scripts
    config['output']['exclude']['names'].append("template_task_local.sh")
    config['output']['exclude']['names'].append("template_task_slurm.sh")
    output = config['output']

    # from here on, make sure we have no configuration errors
    errors = []

    image = None
    if not isinstance(config['image'], str):
        errors.append('Attribute \'image\' must not be a str')
    elif config['image'] == '':
        errors.append('Attribute \'image\' must not be empty')
    else:
        image = config['image']
        if 'docker' in image:
            image_owner, image_name, image_tag = docker.parse_image_components(image)
            if not docker.image_exists(image_name, image_owner, image_tag):
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

    env = []
    if 'env' in config:
        if not all(var != '' for var in config['env']):
            errors.append('Every environment variable must be non-empty')
        else:
            env = [EnvironmentVariable(
                key=variable.rpartition('=')[0],
                value=variable.rpartition('=')[2])
                for variable in config['env']]

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
            input = Input(path=path, kind='files',
                          patterns=config['input']['patterns'] if 'patterns' in config['input'] else None)
        elif kind == 'directory':
            input = Input(path=path, kind='directory',
                          patterns=config['input']['patterns'] if 'patterns' in config['input'] else None)
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
        # if not (
        #         'slurm' in jobqueue or 'yarn' in jobqueue or 'pbs' in jobqueue or 'moab' in jobqueue or 'sge' in jobqueue or 'lsf' in jobqueue or 'oar' in jobqueue or 'kube' in jobqueue):
        #     raise ValueError(f"Unsupported jobqueue configuration: {jobqueue}")

        if 'queue' in jobqueue:
            if not isinstance(jobqueue['queue'], str):
                errors.append('Section \'jobqueue\'.\'queue\' must be a str')
        else:
            jobqueue['queue'] = task.agent.queue
        if 'project' in jobqueue:
            if not isinstance(jobqueue['project'], str):
                errors.append('Section \'jobqueue\'.\'project\' must be a str')
        elif task.agent.project is not None and task.agent.project != '':
            jobqueue['project'] = task.agent.project
        if 'walltime' in jobqueue:
            if not isinstance(jobqueue['walltime'], str):
                errors.append('Section \'jobqueue\'.\'walltime\' must be a str')
        elif 'time' in jobqueue:
            if not isinstance(jobqueue['time'], str):
                errors.append('Section \'jobqueue\'.\'time\' must be a str (note that \'time\' is also deprecated, please use \'walltime\' instead')
        else:
            jobqueue['walltime'] = task.agent.max_walltime
        if 'cores' in jobqueue:
            if not isinstance(jobqueue['cores'], int):
                errors.append('Section \'jobqueue\'.\'cores\' must be a int')
        else:
            jobqueue['cores'] = task.agent.max_cores
        if 'processes' in jobqueue:
            if not isinstance(jobqueue['processes'], int):
                errors.append('Section \'jobqueue\'.\'processes\' must be a int')
        else:
            jobqueue['processes'] = task.agent.max_processes
        if 'header_skip' in jobqueue and not all(extra is str for extra in jobqueue['header_skip']):
            errors.append('Section \'jobqueue\'.\'header_skip\' must be a list of str')
        elif task.agent.header_skip is not None and task.agent.header_skip != '':
            jobqueue['header_skip'] = task.agent.header_skip
        if 'extra' in jobqueue and not all(extra is str for extra in jobqueue['extra']):
            errors.append('Section \'jobqueue\'.\'extra\' must be a list of str')

    shell = None
    if 'shell' in config:
        shell = config['shell']
        if not isinstance(shell, str):
            errors.append('Attribute \'shell\' must be a str')
        elif shell != 'sh' and shell != 'bash' and shell != 'zsh':  # TODO: do we need to support any others?
            errors.append('Attribute \'shell\' must be \'sh\', \'bash\', or \'zsh\'')

    options = TaskOptions(
        workdir=work_dir,
        image=image,
        command=command)

    if input is not None: options['input'] = input
    if output is not None: options['output'] = output
    if parameters is not None: options['parameters'] = parameters
    if env is not None: options['env'] = env
    if bind_mounts is not None: options['bind_mounts'] = bind_mounts
    # if checksums is not None: options['checksums'] = checksums
    if log_file is not None: options['log_file'] = log_file
    if jobqueue is not None: options['jobqueue'] = jobqueue
    if no_cache is not None: options['no_cache'] = no_cache
    if gpu is not None: options['gpus'] = task.agent.gpus
    if shell is not None: options['shell'] = shell

    return errors, options
