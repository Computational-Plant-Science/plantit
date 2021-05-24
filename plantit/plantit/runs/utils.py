import asyncio
import binascii
import json
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
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from plantit.redis import RedisClient
from plantit.runs.models import Run, DelayedRunTask, RepeatingRunTask
from plantit.runs.ssh import SSH
from plantit.resources.models import Resource, ResourceAccessPolicy, ResourceRole
from plantit.resources.utils import map_resource
from plantit.utils import get_repo_config, get_repo_readme


def clean_html(raw_html):
    expr = re.compile('<.*?>')
    text = re.sub(expr, '', raw_html)
    return text


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type())
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

    async_to_sync(get_channel_layer().group_send)(f"runs-{run.user.username}", {
        'type': 'update_status',
        'run': map_run(run),
    })


def stat_logs(id: str):
    log_path = Path(join(environ.get('RUNS_LOGS'), f"{id}.plantit.log"))
    return datetime.fromtimestamp(log_path.stat().st_mtime) if log_path.is_file() else None


def remove_logs(id: str, cluster: str):
    local_log_path = join(environ.get('RUNS_LOGS'), f"{id}.plantit.log")
    # cluster_log_path = join(environ.get('RUNS_LOGS'), f"{id}.{cluster.lower()}.log")
    os.remove(local_log_path)
    # os.remove(cluster_log_path)


def format_workflows(response, token):
    response_json = response.json()
    workflows = [{
        'repo': item['repository'],
        'config': get_repo_config(item['repository']['name'], item['repository']['owner']['login'], token),
        # 'readme': get_repo_readme(item['repository']['name'], item['repository']['owner']['login'], token)
    } for item in response_json['items']] if 'items' in response_json else []
    return workflows


async def list_workflows_for_users(usernames: List[str], token: str):
    urls = [f"https://api.github.com/search/code?q=filename:plantit.yaml+user:{username}" for username in usernames]
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
    }

    async with httpx.AsyncClient(headers=headers) as client:
        futures = [client.get(url) for url in urls]
        responses = await asyncio.gather(*futures)
        return [workflow for workflows in [format_workflows(response, token) for response in responses] for workflow in workflows]


def list_workflows_for_user(username: str, token: str):
    response = requests.get(
        f"https://api.github.com/search/code?q=filename:plantit.yaml+user:{username}",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
        })
    workflows = format_workflows(response, token)
    return [flow for flow in workflows]


def map_old_workflow_config_to_new(old_config: dict, run: Run, resources: dict):
    new_config = {
        'image': old_config['config']['image'],
        'command': old_config['config']['commands'],
        'workdir': old_config['config']['workdir'],
        'log_file': f"{run.guid}.{run.resource.name.lower()}.log"
    }

    del old_config['config']['cluster']

    if 'mount' in old_config['config']:
        new_config['bind_mounts'] = old_config['config']['mount']

    if 'parameters' in old_config['config']:
        old_params = old_config['config']['parameters']
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
        new_config['parameters'] = params

    if 'input' in old_config['config']:
        input_kind = old_config['config']['input']['kind'] if 'kind' in old_config['config']['input'] else None
        new_config['input'] = dict()
        if input_kind == 'directory':
            new_config['input']['directory'] = dict()
            new_config['input']['directory']['path'] = join(run.resource.workdir, run.workdir, 'input')
            new_config['input']['directory']['patterns'] = old_config['config']['input']['patterns']
        elif input_kind == 'files':
            new_config['input']['files'] = dict()
            new_config['input']['files']['path'] = join(run.resource.workdir, run.workdir, 'input')
            new_config['input']['files']['patterns'] = old_config['config']['input']['patterns']
        elif input_kind == 'file':
            new_config['input']['file'] = dict()
            new_config['input']['file']['path'] = join(run.resource.workdir, run.workdir, 'input',
                                                       old_config['config']['input']['from'].rpartition('/')[2])

    sandbox = run.resource.name == 'Sandbox'
    work_dir = join(run.resource.workdir, run.workdir)
    if not sandbox and not run.resource.job_array:
        new_config['jobqueue'] = dict()
        new_config['jobqueue']['slurm'] = {
            'cores': resources['cores'],
            'processes': resources['processes'],
            'walltime': resources['time'],
            'local_directory': work_dir,
            'log_directory': work_dir,
            'env_extra': [run.resource.pre_commands]
        }

        if 'mem' in resources:
            new_config['jobqueue']['slurm']['memory'] = resources['mem']
        if run.resource.queue is not None and run.resource.queue != '':
            new_config['jobqueue']['slurm']['queue'] = run.resource.queue
        if run.resource.project is not None and run.resource.project != '':
            new_config['jobqueue']['slurm']['project'] = run.resource.project
        if run.resource.header_skip is not None and run.resource.header_skip != '':
            new_config['jobqueue']['slurm']['header_skip'] = run.resource.header_skip.split(',')

        if 'gpu' in old_config['config'] and old_config['config']['gpu']:
            if run.resource.gpu:
                print(f"Using GPU on {run.resource.name} queue '{run.resource.gpu_queue}'")
                new_config['gpu'] = True
                new_config['jobqueue']['slurm']['job_extra'] = [f"--gres=gpu:1"]
                new_config['jobqueue']['slurm']['queue'] = run.resource.gpu_queue
            else:
                print(f"No GPU support on {run.resource.name}")

    return new_config


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


def map_run(run: Run):
    submission_log_file = submission_log_file_path(run)

    if Path(submission_log_file).is_file():
        with open(submission_log_file, 'r') as log:
            submission_logs = [line.strip() for line in log.readlines()[-int(1000000):]]
    else:
        submission_logs = []

    try:
        ResourceAccessPolicy.objects.get(user=run.user, cluster=run.resource, role__in=[ResourceRole.own, ResourceRole.run])
        can_restart = True
    except:
        can_restart = False

    results = RedisClient.get().get(f"results/{run.guid}")

    return {
        'can_restart': can_restart,
        'id': run.guid,
        'job_id': run.job_id,
        'job_status': run.job_status,
        'job_walltime': run.job_elapsed_walltime,
        'work_dir': run.workdir,
        'submission_logs': submission_logs,
        'cluster': run.resource.name,
        'created': run.created.isoformat(),
        'updated': run.updated.isoformat(),
        'completed': run.completed.isoformat() if run.completed is not None else None,
        'workflow_owner': run.workflow_owner,
        'workflow_name': run.workflow_name,
        'tags': [str(tag) for tag in run.tags.all()],
        'is_complete': run.is_complete,
        'is_success': run.is_success,
        'is_failure': run.is_failure,
        'is_cancelled': run.is_cancelled,
        'is_timeout': run.is_timeout,
        'workflow_image_url': run.workflow_image_url,
        'result_previews_loaded': run.previews_loaded,
        'cleaned_up': run.cleaned_up,
        'output_files': json.loads(results) if results is not None else None
    }


def submission_log_file_path(run: Run):
    return join(os.environ.get('RUNS_LOGS'), f"{run.guid}.plantit.log")


def container_log_file_name(run: Run):
    if run.resource.launcher:
        return f"plantit.{run.job_id}.out"
    else:
        return f"{run.guid}.{run.resource.name.lower()}.log"


def container_log_file_path(run: Run):
    return join(os.environ.get('RUNS_LOGS'), container_log_file_name(run))


def create_run(username: str, cluster_name: str, workflow: dict) -> Run:
    now = timezone.now()
    user = User.objects.get(username=username)
    cluster = Resource.objects.get(name=cluster_name)
    workflow_owner = workflow['repo']['owner']['login']
    workflow_name = workflow['repo']['name']
    workflow_config = get_repo_config(workflow_name, workflow_owner, user.profile.github_token)
    run = Run.objects.create(
        guid=str(uuid.uuid4()),
        user=user,
        workflow_owner=workflow_owner,
        workflow_name=workflow_name,
        cluster=cluster,
        job_status='CREATED',
        created=now,
        updated=now,
        token=binascii.hexlify(os.urandom(20)).decode())

    if 'logo' in workflow_config:
        run.workflow_image_url = f"https://raw.githubusercontent.com/{workflow_owner}/{workflow_name}/master/{workflow_config['logo']}"

    # add tags
    for tag in workflow['config']['tags']:
        run.tags.add(tag)

    # guid for working directory name
    run.workdir = f"{run.guid}/"
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
        'cluster': map_resource(task.resource),
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
        'cluster': map_resource(task.resource),
        'name': task.name,
        'eta': task.eta,
        'interval': {
            'every': task.interval.every,
            'period': task.interval.period
        },
        'enabled': task.enabled,
        'last_run': task.last_run_at
    }


def get_run_results(run: Run, workflow: dict):
    included_by_name = ((workflow['output']['include']['names'] if 'names' in workflow['output'][
        'include'] else [])) if 'output' in workflow else []  # [f"{run.task_id}.zip"]
    included_by_name.append(f"{run.guid}.zip")  # zip file
    if not run.resource.launcher:
        included_by_name.append(f"{run.guid}.{run.resource.name.lower()}.log")
    if run.job_id is not None and run.job_id != '':
        included_by_name.append(f"plantit.{run.job_id}.out")
        included_by_name.append(f"plantit.{run.job_id}.err")
    included_by_pattern = (
        workflow['output']['include']['patterns'] if 'patterns' in workflow['output']['include'] else []) if 'output' in workflow else []

    client = SSH(run.resource.hostname, run.resource.port, run.resource.username)
    work_dir = join(run.resource.workdir, run.workdir)
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


def get_job_walltime(run: Run) -> (str, str):
    ssh = SSH(run.resource.hostname, run.resource.port, run.resource.username)
    with ssh:
        lines = execute_command(
            ssh_client=ssh,
            pre_command=":",
            command=f"squeue --user={run.resource.username}",
            directory=join(run.resource.workdir, run.workdir),
            allow_stderr=True)

        try:
            job_line = next(l for l in lines if run.job_id in l)
            job_split = job_line.split()
            job_walltime = job_split[-3]
            return job_walltime
        except StopIteration:
            return None


def get_job_status(run: Run) -> str:
    ssh = SSH(run.resource.hostname, run.resource.port, run.resource.username)
    with ssh:
        lines = execute_command(
            ssh_client=ssh,
            pre_command=':',
            command=f"sacct -j {run.job_id}",
            directory=join(run.resource.workdir, run.workdir),
            allow_stderr=True)

        job_line = next(l for l in lines if run.job_id in l)
        job_split = job_line.split()
        job_status = job_split[5].replace('+', '')
        return job_status
    pass


def cancel_run(run: Run):
    ssh = SSH(run.resource.hostname, run.resource.port, run.resource.username)
    with ssh:
        if run.job_id is None or not any([run.job_id in r for r in execute_command(
                ssh_client=ssh,
                pre_command=':',
                command=f"squeue -u {run.resource.username}",
                directory=join(run.resource.workdir, run.workdir))]):
            # run doesn't exist, so no need to cancel
            return

        execute_command(
            ssh_client=ssh,
            pre_command=':',
            command=f"scancel {run.job_id}",
            directory=join(run.resource.workdir, run.workdir))