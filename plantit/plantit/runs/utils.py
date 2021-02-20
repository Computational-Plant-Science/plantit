import asyncio
import os
import re
from datetime import timedelta, datetime
from os import environ
from os.path import join
from pathlib import Path
from typing import List

import httpx
import requests
from requests.auth import HTTPBasicAuth

from plantit import settings
from plantit.runs.models import Run
from plantit.runs.ssh import SSH
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


def update_local_logs(id: str, description: str):
    log_path = join(environ.get('RUNS_LOGS'), f"{id}.plantit.log")
    with open(log_path, 'a') as log:
        log.write(f"{description}\n")


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


def map_run(run: Run):
    return {
        'id': run.guid,
        'job_id': run.job_id,
        'job_status': run.job_status,
        'job_walltime': run.job_walltime,
        'work_dir': run.work_dir,
        'target': run.target.name,
        'created': run.created,
        'updated': run.updated,
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
