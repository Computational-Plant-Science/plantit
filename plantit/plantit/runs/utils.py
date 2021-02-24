import asyncio
import binascii
import os
import re
import tempfile
import uuid
from datetime import timedelta, datetime
from dateutil import parser
from os import environ
from os.path import join
from pathlib import Path
from typing import List

import httpx
import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from django.utils import timezone
from requests.auth import HTTPBasicAuth

from plantit import settings
from plantit.runs.models import Run, DelayedRunTask, RepeatingRunTask
from plantit.runs.ssh import SSH
from plantit.targets.models import Target
from plantit.targets.utils import map_target
from plantit.utils import get_repo_config, get_repo_config_internal


def clean_html(raw_html):
    expr = re.compile('<.*?>')
    text = re.sub(expr, '', raw_html)
    return text


def execute_command(ssh_client: SSH, pre_command: str, command: str, directory: str, allow_stderr: bool = False) -> List[str]:
    full_command = f"{pre_command} && cd {directory} && {command}" if directory else command
    output = []
    errors = []

    print(f"Executing command on '{ssh_client.host}': {full_command}")
    stdin, stdout, stderr = ssh_client.client.exec_command(full_command, get_pty=True)
    stdin.close()

    for line in iter(lambda: stdout.readline(2048), ""):
        clean = clean_html(line)
        output.append(clean)
        print(f"Received stdout from '{ssh_client.host}': '{clean}'")
    for line in iter(lambda: stderr.readline(2048), ""):
        clean = clean_html(line)
        if 'WARNING' not in clean:  # Dask occasionally returns messages like 'distributed.worker - WARNING - Heartbeat to scheduler failed'
            errors.append(clean)
            print(f"Received stderr from '{ssh_client.host}': '{clean}'")
    if stdout.channel.recv_exit_status() != 0:
        raise Exception(f"Received non-zero exit status from '{ssh_client.host}'")
    elif not allow_stderr and len(errors) > 0:
        raise Exception(f"Received stderr: {errors}")

    return output


def update_status(run: Run, description: str):
    log_path = join(environ.get('RUNS_LOGS'), f"{run.guid}.plantit.log")
    with open(log_path, 'a') as log:
        log.write(f"{description}\n")

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(run.guid, {
        'type': 'update_status',
        'run': map_run(run, True),
    })


def stat_logs(id: str):
    log_path = Path(join(environ.get('RUNS_LOGS'), f"{id}.plantit.log"))
    return datetime.fromtimestamp(log_path.stat().st_mtime) if log_path.is_file() else None


def remove_logs(id: str, target: str):
    local_log_path = join(environ.get('RUNS_LOGS'), f"{id}.plantit.log")
    # target_log_path = join(environ.get('RUNS_LOGS'), f"{id}.{target.lower()}.log")
    os.remove(local_log_path)
    # os.remove(target_log_path)


def get_flows(response, token):
    response_json = response.json()
    flows = [{
        'repo': item['repository'],
        'config': get_repo_config(item['repository']['name'], item['repository']['owner']['login'], token)
    } for item in response_json['items']] if 'items' in response_json else []
    return flows


async def list_flows_for_users(usernames: List[str], token: str):
    urls = [f"https://api.github.com/search/code?q=filename:plantit.yaml+user:{username}" for username in usernames]
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
    }
    async with httpx.AsyncClient(headers=headers) as client:
        futures = [client.get(url) for url in urls]
        responses = await asyncio.gather(*futures)
        return [flow for flows in [get_flows(response, token) for response in responses] for flow in flows]


def list_flows_for_user(username: str, token: str):
    response = requests.get(
        f"https://api.github.com/search/code?q=filename:plantit.yaml+user:{username}",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
        })
    flows = get_flows(response, token)
    return [flow for flow in flows]  # if flow['config']['public']]


def list_by_user_internal(username):
    response = requests.get(
        f"https://api.github.com/search/code?q=filename:plantit.yaml+user:{username}",
        auth=HTTPBasicAuth(settings.GITHUB_USERNAME, settings.GITHUB_KEY),
        headers={
            "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
        })
    flows = [{
        'repo': item['repository'],
        'config': get_repo_config_internal(item['repository']['name'], item['repository']['owner']['login'])
    } for item in response.json()['items']]

    return [flow for flow in flows if flow['config']['public']]


def old_flow_config_to_new(flow: dict, run: Run, resources: dict):
    new_flow = {
        'image': flow['config']['image'],
        'command': flow['config']['commands'],
        'workdir': flow['config']['workdir'],
        'log_file': f"{run.guid}.{run.target.name.lower()}.log"
    }

    del flow['config']['target']

    if 'mount' in flow['config']:
        new_flow['bind_mounts'] = flow['config']['mount']

    if 'parameters' in flow['config']:
        new_flow['parameters'] = flow['config']['parameters']

    if 'input' in flow['config']:
        input_kind = flow['config']['input']['kind'] if 'kind' in flow['config']['input'] else None
        new_flow['input'] = dict()
        if input_kind == 'directory':
            new_flow['input']['directory'] = dict()
            new_flow['input']['directory']['path'] = join(run.target.workdir, run.work_dir, 'input')
            new_flow['input']['directory']['patterns'] = flow['config']['input']['patterns']
        elif input_kind == 'files':
            new_flow['input']['files'] = dict()
            new_flow['input']['files']['path'] = join(run.target.workdir, run.work_dir, 'input')
            new_flow['input']['files']['patterns'] = flow['config']['input']['patterns']
        elif input_kind == 'file':
            new_flow['input']['file'] = dict()
            new_flow['input']['file']['path'] = join(run.target.workdir, run.work_dir, 'input', flow['config']['input']['from'].rpartition('/')[2])

    sandbox = run.target.name == 'Sandbox'
    work_dir = join(run.target.workdir, run.work_dir)
    if not sandbox:
        new_flow['jobqueue'] = dict()
        new_flow['jobqueue']['slurm'] = {
            'cores': resources['cores'],
            'processes': resources['processes'],
            'walltime': resources['time'],
            'local_directory': work_dir,
            'log_directory': work_dir,
            'env_extra': [run.target.pre_commands]
        }

        if 'mem' in resources:
            new_flow['jobqueue']['slurm']['memory'] = resources['mem']
        if run.target.queue is not None and run.target.queue != '':
            new_flow['jobqueue']['slurm']['queue'] = run.target.queue
        if run.target.project is not None and run.target.project != '':
            new_flow['jobqueue']['slurm']['project'] = run.target.project
        if run.target.header_skip is not None and run.target.header_skip != '':
            new_flow['jobqueue']['slurm']['header_skip'] = run.target.header_skip.split(',')

        if 'gpu' in flow['config'] and flow['config']['gpu']:
            if run.target.gpu:
                new_flow['gpu'] = True
                new_flow['jobqueue']['slurm']['job_extra'] = [f"--gres=gpu:K40:1"]
                new_flow['jobqueue']['slurm']['queue'] = run.target.gpu_queue
            else:
                print(f"No GPU support on {run.target.name}")

    return new_flow


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


def map_run_task(task):
    return {
        'name': task.name,
        'run': map_run(task.run),
        # 'crontab': task.crontab if task.crontab is not None else None,
        'interval': {
            'every': task.interval.every,
            'period': task.interval.period
        } if task.interval is not None else None,
        'enabled': task.enabled,
        'last_run': task.last_run_at
    }


def map_run(run: Run, get_container_logs: bool = False):
    work_dir = join(run.target.workdir, run.work_dir)
    ssh_client = SSH(run.target.hostname, run.target.port, run.target.username)
    submission_log_file = submission_log_file_name(run)
    container_log_file = container_log_file_name(run)

    if Path(submission_log_file).is_file():
        with open(submission_log_file, 'r') as log:
            submission_logs = [line.strip() for line in log.readlines()[-int(1000000):]]
    else:
        submission_logs = []

    if get_container_logs:
        with ssh_client:
            with ssh_client.client.open_sftp() as sftp:
                stdin, stdout, stderr = ssh_client.client.exec_command('test -e {0} && echo exists'.format(join(work_dir, container_log_file)))
                errs = stderr.read()
                if errs:
                    raise Exception(f"Failed to check existence of {container_log_file}: {errs}")
                if not stdout.read().decode().strip() == 'exists':
                    container_logs = []
                else:
                    with tempfile.NamedTemporaryFile() as tf:
                        sftp.chdir(work_dir)
                        sftp.get(container_log_file, tf.name)
                        with open(tf.name, 'r') as file:
                            container_logs = [line.strip() for line in file.readlines()[-int(1000000):]]
    else:
        container_logs = []

    return {
        'id': run.guid,
        'job_id': run.job_id,
        'job_status': run.job_status,
        'job_walltime': run.job_walltime,
        'work_dir': run.work_dir,
        'submission_logs': submission_logs,
        'container_logs': container_logs,
        'target': run.target.name,
        'created': run.created.isoformat(),
        'updated': run.updated.isoformat(),
        'flow_owner': run.flow_owner,
        'flow_name': run.flow_name,
        'tags': [str(tag) for tag in run.tags.all()],
        'is_complete': run.is_complete,
        'is_success': run.is_success,
        'is_failure': run.is_failure,
        'is_cancelled': run.is_cancelled,
        'is_timeout': run.is_timeout,
        'flow_image_url': run.flow_image_url
    }


def submission_log_file_name(run: Run):
    return join(os.environ.get('RUNS_LOGS'), f"{run.guid}.plantit.log")


def container_log_file_name(run: Run):
    return f"{run.guid}.{run.target.name.lower()}.log"


def create_run(username: str, target_name: str, flow: dict) -> Run:
    now = timezone.now()
    user = User.objects.get(username=username)
    target = Target.objects.get(name=target_name)
    flow_owner = flow['repo']['owner']['login']
    flow_name = flow['repo']['name']
    flow_config = get_repo_config(flow_name, flow_owner, user.profile.github_token)
    run = Run.objects.create(
        guid=str(uuid.uuid4()),
        user=user,
        flow_owner=flow_owner,
        flow_name=flow_name,
        flow_image_url=f"https://raw.githubusercontent.com/{flow_owner}/{flow_name}/master/{flow_config['logo']}",
        target=target,
        job_status='CREATED',
        created=now,
        updated=now,
        token=binascii.hexlify(os.urandom(20)).decode())

    # add tags
    for tag in flow['config']['tags']:
        run.tags.add(tag)

    # guid for working directory name
    run.work_dir = f"{run.guid}/"

    run.save()
    return run


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


def map_delayed_run_task(task: DelayedRunTask):
    return {
        'target': map_target(task.target),
        'name': task.name,
        'eta': task.eta,
        'interval': {
            'every': task.interval.every,
            'period': task.interval.period
        },
        'last_run': task.last_run_at
    }


def map_repeating_run_task(task: RepeatingRunTask):
    return {
        'target': map_target(task.target),
        'name': task.name,
        'eta': task.eta,
        'interval': {
            'every': task.interval.every,
            'period': task.interval.period
        },
        'enabled': task.enabled,
        'last_run': task.last_run_at
    }
