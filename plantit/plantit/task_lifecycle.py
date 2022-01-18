import os
import subprocess
import tempfile
import logging
from os import environ
from os.path import join
from pathlib import Path
from typing import List

import binascii
import json
import uuid
from datetime import timedelta

import yaml
from asgiref.sync import async_to_sync

from django.contrib.auth.models import User
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTasks

from plantit.agents.models import Agent, AgentScheduler
from plantit.miappe.models import Investigation, Study
from plantit.redis import RedisClient
from plantit.ssh import SSH, execute_command
from plantit.task_logging import log_task_orchestrator_status
from plantit.task_resources import get_task_ssh_client, push_task_channel_event
from plantit.task_scripts import compose_task_run_script, compose_task_launcher_script
from plantit.tasks.models import DelayedTask, RepeatingTask, Task, TaskStatus, TaskCounter, PlantITCLIOptions, InputKind
from plantit.utils.misc import del_none
from plantit.utils.tasks import parse_task_eta, parse_time_limit_seconds, parse_task_job_id, \
    get_task_scheduler_log_file_path, get_task_scheduler_log_file_name
from plantit.task_configuration import parse_task_cli_options
from plantit.keypairs import get_user_private_key_path

logger = logging.getLogger(__name__)


def create_task(username: str,
                agent_name: str,
                workflow: dict,
                branch: dict,
                name: str = None,
                guid: str = None,
                project: str = None,
                study: str = None):
    repo_owner = workflow['repo']['owner']['login']
    repo_name = workflow['repo']['name']
    repo_branch = branch['name']
    agent = Agent.objects.get(name=agent_name)
    user = User.objects.get(username=username)
    if guid is None: guid = str(uuid.uuid4())  # if the browser client hasn't set a GUID, create one
    now = timezone.now()

    time_limit = parse_time_limit_seconds(workflow['config']['time'])
    logger.info(f"Using task time limit {time_limit}s")
    due_time = timezone.now() + timedelta(seconds=time_limit)

    task = Task.objects.create(
        guid=guid,
        name=guid if name is None else name,
        user=user,
        workflow=workflow,
        workflow_owner=repo_owner,
        workflow_name=repo_name,
        workflow_branch=repo_branch,
        agent=agent,
        status=TaskStatus.CREATED,
        created=now,
        updated=now,
        due_time=due_time,
        token=binascii.hexlify(os.urandom(20)).decode())

    # add MIAPPE info
    if project is not None: task.project = Investigation.objects.get(owner=user, title=project)
    if study is not None: task.study = Study.objects.get(project=task.project, title=study)

    # add repo logo
    if 'logo' in workflow['config']:
        logo_path = workflow['config']['logo']
        task.workflow_image_url = f"https://raw.githubusercontent.com/{repo_owner}/{repo_name}/master/{logo_path}"

    for tag in workflow['config']['tags']: task.tags.add(tag)  # add task tags
    task.workdir = f"{task.guid}/"  # use GUID for working directory name
    task.save()

    counter = TaskCounter.load()
    counter.count = counter.count + 1
    counter.save()

    return task


def create_immediate_task(user: User, workflow):
    repo_owner = workflow['repo']['owner']['login']
    repo_name = workflow['repo']['name']
    repo_branch = workflow['branch']['name']

    redis = RedisClient.get()
    last_config = workflow.copy()
    del last_config['auth']
    last_config['timestamp'] = timezone.now().isoformat()
    redis.set(f"workflow_configs/{user.username}/{repo_owner}/{repo_name}/{repo_branch}", json.dumps(last_config))

    config = workflow['config']
    branch = workflow['branch']
    task_guid = config.get('task_guid', None) if workflow['type'] == 'Now' else str(uuid.uuid4())
    task_name = task_guid
    # task_name = config.get('task_name', None)

    agent = Agent.objects.get(name=config['agent']['name'])
    task = create_task(
        username=user.username,
        agent_name=agent.name,
        workflow=workflow,
        branch=branch,
        name=task_name if task_name is not None and task_name != '' else task_guid,
        guid=task_guid,
        project=workflow['miappe']['project']['title'] if workflow['miappe']['project'] is not None else None,
        study=workflow['miappe']['study']['title'] if workflow['miappe']['study'] is not None else None)

    return task


def create_delayed_task(user: User, workflow):
    now = timezone.now().timestamp()
    id = f"{user.username}-delayed-{now}"
    eta, seconds = parse_task_eta(workflow)
    schedule, _ = IntervalSchedule.objects.get_or_create(every=seconds, period=IntervalSchedule.SECONDS)

    repo_owner = workflow['repo']['owner']['login']
    repo_name = workflow['repo']['name']
    repo_branch = workflow['branch']['name']

    if 'logo' in workflow['config']:
        logo_path = workflow['config']['logo']
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
        args=json.dumps([user.username, workflow, id]))

    # manually refresh task schedule
    PeriodicTasks.changed(task)

    return task, created


def create_repeating_task(user: User, workflow):
    now = timezone.now().timestamp()
    id = f"{user.username}-repeating-{now}"
    eta, seconds = parse_task_eta(workflow)
    schedule, _ = IntervalSchedule.objects.get_or_create(every=seconds, period=IntervalSchedule.SECONDS)

    repo_owner = workflow['repo']['owner']['login']
    repo_name = workflow['repo']['name']
    repo_branch = workflow['branch']['name']

    if 'logo' in workflow['config']:
        logo_path = workflow['config']['logo']
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


def configure_task_environment(task: Task, ssh: SSH):
    log_task_orchestrator_status(task, [f"Verifying configuration"])
    async_to_sync(push_task_channel_event)(task)

    parse_errors, cli_options = parse_task_cli_options(task)

    if len(parse_errors) > 0: raise ValueError(f"Failed to parse task options: {' '.join(parse_errors)}")

    work_dir = join(task.agent.workdir, task.guid)
    log_task_orchestrator_status(task, [f"Creating working directory"])
    async_to_sync(push_task_channel_event)(task)

    list(execute_command(ssh=ssh, precommand=':', command=f"mkdir {work_dir}"))

    log_task_orchestrator_status(task, [f"Uploading task"])
    upload_task_script(task, ssh, cli_options)
    async_to_sync(push_task_channel_event)(task)


def upload_task_script(task: Task, ssh: SSH, options: PlantITCLIOptions):
    # task working directory
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
        lines = compose_task_run_script(task, options, environ.get(
            'TASKS_TEMPLATE_SCRIPT_LOCAL') if task.agent.scheduler == AgentScheduler.LOCAL else environ.get(
            'TASKS_TEMPLATE_SCRIPT_SLURM'))
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
        # set default directory for input files
        if 'input' in options:
            path = options['input']['path']
            kind = options['input']['kind']
            many = kind == InputKind.DIRECTORY or kind == InputKind.FILES
            options['input']['path'] = 'input' if path == '' or many else f"input/{path.rpartition('/')[2]}"

        # TODO support for more schedulers
        options['jobqueue'] = {'slurm': options['jobqueue']}

        # upload the config file for the CLI
        logger.info(f"Uploading config for task {task.guid}")
        with ssh.client.open_sftp() as sftp:
            sftp.chdir(work_dir)
            with sftp.open(f"{task.guid}.yaml", 'w') as cli_file:
                yaml.dump(del_none(options), cli_file, default_flow_style=False)


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
        if task.agent.scheduler != AgentScheduler.LOCAL:
            lines = []
            for line in execute_command(
                    ssh=ssh,
                    precommand=':',
                    command=f"squeue -u {task.agent.username}",
                    directory=join(task.agent.workdir, task.workdir),
                    allow_stderr=True):
                logger.info(line)
                lines.append(line)

            if task.job_id is None or not any([task.job_id in r for r in lines]):
                return  # run doesn't exist, so no need to cancel

            # TODO support PBS/other scheduler cancellation commands, not just SLURM
            execute_command(
                ssh=ssh,
                precommand=':',
                command=f"scancel {task.job_id}",
                directory=join(task.agent.workdir, task.workdir))


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


def get_job_walltime(task: Task) -> (str, str):
    ssh = get_task_ssh_client(task)
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


def get_job_status(task: Task) -> str:
    ssh = get_task_ssh_client(task)
    with ssh:
        lines = execute_command(
            ssh=ssh,
            precommand=':',
            command=f"sacct -j {task.job_id}",
            directory=join(task.agent.workdir, task.workdir),
            allow_stderr=True)

        line = next(l for l in lines if task.job_id in l)
        status = line.split()[5].replace('+', '')

        # check the scheduler log file in case `sacct` is no longer displaying info
        # about this job so we don't miss a cancellation/timeout/failure/completion
        with ssh.client.open_sftp() as sftp:

            log_file_path = get_task_scheduler_log_file_path(task)
            stdin, stdout, stderr = ssh.client.exec_command(f"test -e {log_file_path} && echo exists")
            if stdout.read().decode().strip() != 'exists': return status

            with sftp.open(log_file_path, 'r') as log_file:
                logger.info(f"Checking scheduler log file {log_file_path} for job {task.job_id} status")
                for line in log_file.readlines():
                    if 'CANCELLED' in line or 'CANCELED' in line:
                        status = 'CANCELED'
                        continue
                    if 'TIMEOUT' in line:
                        status = 'TIMEOUT'
                        continue
                    if 'FAILED' in line or 'FAILURE' in line or 'NODE_FAIL' in line:
                        status = 'FAILED'
                        break
                    if 'SUCCESS' in line or 'COMPLETED' in line:
                        status = 'SUCCESS'
                        break

                return status


def list_result_files(task: Task, workflow: dict) -> List[dict]:
    """
    Lists result files expected to be produced by the given task (assumes the task has completed). Returns a dict with form `{'name': <name>, 'path': <full path>, 'exists': <True or False>}`

    Args:
        task: The task
        workflow: The task's workflow

    Returns: Files expected to be produced by the task

    """

    # TODO factor out into method
    included_by_name = ((workflow['output']['include']['names'] if 'names' in workflow['output'][
        'include'] else [])) if 'output' in workflow else []  # [f"{run.task_id}.zip"]
    included_by_name.append(f"{task.guid}.zip")  # zip file
    if not task.agent.launcher:
        included_by_name.append(f"{task.guid}.{task.agent.name.lower()}.log")
    if task.agent.scheduler != AgentScheduler.LOCAL and task.job_id is not None and task.job_id != '':
        included_by_name.append(f"plantit.{task.job_id}.out")
        included_by_name.append(f"plantit.{task.job_id}.err")
    included_by_pattern = (
        workflow['output']['include']['patterns'] if 'patterns' in workflow['output'][
            'include'] else []) if 'output' in workflow else []

    ssh = get_task_ssh_client(task)
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

            logger.info(f"Looking for files by pattern(s): {', '.join(included_by_pattern)}")

            for f in sftp.listdir(workdir):
                if any(pattern in f for pattern in included_by_pattern):
                    if not any(s == f for s in seen):
                        outputs.append({
                            'name': f,
                            'path': join(workdir, f),
                            'exists': True
                        })

    logger.info(f"Expecting {len(outputs)} result files for task {task.guid}: {', '.join([o['name'] for o in outputs])}")
    return outputs
