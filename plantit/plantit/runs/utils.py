import asyncio
import json
import os
import re
import traceback
from os.path import join

from datetime import datetime, timedelta
from pprint import pprint
from typing import List

import httpx
import requests
import yaml
from django.contrib.auth.models import User
from django.utils import timezone
from requests.auth import HTTPBasicAuth
from celery.exceptions import SoftTimeLimitExceeded

from plantit import settings
from plantit.celery import app
from plantit.runs.models import Run, Status
from plantit.runs.ssh import SSH
from plantit.utils import get_repo_config, get_repo_config_internal


def clean_html(raw_html):
    expr = re.compile('<.*?>')
    text = re.sub(expr, '', raw_html)
    return text


def execute_command(ssh_client: SSH, pre_command: str, command: str, directory: str):
    full_command = f"{pre_command} && cd {directory} && {command}" if directory else command
    print(f"Executing command on '{ssh_client.host}': {full_command}")
    stdin, stdout, stderr = ssh_client.client.exec_command(full_command)
    stdin.close()

    errors = []
    for line in iter(lambda: stdout.readline(2048), ""):
        print(f"Received stdout from '{ssh_client.host}': '{clean_html(line)}'")
    for line in iter(lambda: stderr.readline(2048), ""):
        clean_line = clean_html(line)
        errors.append(clean_line)
        print(f"Received stderr from '{ssh_client.host}': '{clean_line}'")
    if stdout.channel.recv_exit_status() != 0:
        raise Exception(f"Received non-zero exit status from '{ssh_client.host}'")
    elif len(errors) > 0:
        raise Exception(f"Received stderr: {errors}")


def update_status(run: Run, state: int, description: str):
    print(description)
    run.status_set.create(description=description, state=state, location='PlantIT')
    run.save()


def __get_flows(response, token):
    response_json = response.json()
    flows = [{
        'repo': item['repository'],
        'config': get_repo_config(item['repository']['name'], item['repository']['owner']['login'], token)
    } for item in response_json['items']] if 'items' in response_json else []
    return flows


async def __list_all_by_user(usernames: List[str], token: str):
    urls = [f"https://api.github.com/search/code?q=filename:plantit.yaml+user:{username}" for username in usernames]
    headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
        }
    async with httpx.AsyncClient(headers=headers) as client:
        futures = [client.get(url) for url in urls]
        responses = await asyncio.gather(*futures)
        return [flow for flows in [__get_flows(response, token) for response in responses] for flow in flows]


def __list_by_user(username: str, token: str):
    response = requests.get(
        f"https://api.github.com/search/code?q=filename:plantit.yaml+user:{username}",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
        })
    flows = __get_flows(response, token)
    return [flow for flow in flows]  # if flow['config']['public']]


def __list_by_user_internal(username):
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


def __old_flow_config_to_new(flow: dict, run: Run, resources: dict):
    new_flow = {
        'image': flow['config']['image'],
        'command': flow['config']['command'],
        'workdir': flow['config']['workdir'],
        'log_file': f"{run.identifier}.log"
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
            'processes': resources['tasks'],
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
                new_flow['jobqueue']['slurm']['extra'] = [f"--gres=gpu:{resources['cores']}"]
                new_flow['jobqueue']['slurm']['queue'] = run.target.gpu_queue
            else:
                update_status(run, Status.RUNNING, f"No GPU support on {run.target.name}")

    return new_flow


@app.task()
def cleanup(run_id, plantit_token, cyverse_token):
    print(f"TODO: check if run '{run_id}' has completed or timed out on the cluster, retry it with longer walltime, etc")


@app.task()
def execute(flow, run_id, plantit_token, cyverse_token):
    try:
        run = Run.objects.get(identifier=run_id)
        run.started = timezone.now()
        run.save()

        # if flow has outputs, make sure we don't push configuration or job scripts
        if 'output' in flow['config']:
            flow['config']['output']['exclude']['names'] = [
                "flow.yaml",
                "template_local_run.sh",
                "template_slurm_run.sh"]

        # pull cluster resoures out
        if 'resources' not in flow['config']['target']:
            resources = None
        else:
            resources = flow['config']['target']['resources']

        # TODO use this new format from browser
        new_flow = __old_flow_config_to_new(flow, run, resources)

        client = SSH(run.target.hostname, run.target.port, run.target.username)
        work_dir = join(run.target.workdir, run.work_dir)

        with client:
            update_status(run, Status.CREATING, f"Creating working directory '{work_dir}'")
            execute_command(ssh_client=client,
                            pre_command=':',
                            command=f"mkdir {work_dir}",
                            directory=run.target.workdir)

            with client.client.open_sftp() as sftp:
                sftp.chdir(work_dir)

                update_status(run, Status.CREATING, "Uploading configuration")
                # TODO refactor to allow multiple cluster schedulers
                sandbox = run.target.name == 'Sandbox'  # for now, we're either in the sandbox or on a SLURM cluster
                template = os.environ.get('CELERY_TEMPLATE_LOCAL_RUN_SCRIPT') if sandbox else os.environ.get('CELERY_TEMPLATE_SLURM_RUN_SCRIPT')
                template_name = template.split('/')[-1]

                with sftp.open('flow.yaml', 'w') as flow_file:

                    yaml.dump(new_flow, flow_file, default_flow_style=False)

                    # if not sandbox:
                    #     flow['jobqueue']['slurm'] = {
                    #         'cores': resources['cores'],
                    #         'processes': resources['tasks'],
                    #         'walltime': resources['time'],
                    #         'local_directory': work_dir,
                    #         'log_directory': work_dir,
                    #         'env_extra': [run.target.pre_commands]
                    #     }

                    #     if 'mem' in resources:
                    #         flow['jobqueue']['slurm']['memory'] = resources['mem']
                    #     if run.target.queue is not None and run.target.queue != '':
                    #         flow['jobqueue']['slurm']['queue'] = run.target.queue
                    #     if run.target.project is not None and run.target.project != '':
                    #         flow['jobqueue']['slurm']['project'] = run.target.project
                    #     if run.target.header_skip is not None and run.target.header_skip != '':
                    #         flow['jobqueue']['slurm']['header_skip'] = run.target.header_skip.split(',')

                    # if 'gpu' in flow['config'] and flow['config']['gpu']:
                    #     if run.target.gpu:
                    #         flow['jobqueue']['slurm']['extra'] = [f"--gres=gpu:{resources['cores']}"]
                    #         flow['jobqueue']['slurm']['queue'] = run.target.gpu_queue
                    #     else:
                    #         update_status(run, Status.RUNNING, f"No GPU support on {run.target.name}")

                    # yaml.dump(flow['config'], flow_file, default_flow_style=False)

                with open(template, 'r') as template_script, sftp.open(template_name, 'w') as script:
                    for line in template_script:
                        script.write(line)

                    if not sandbox:  # we're on a SLURM cluster
                        script.write("#SBATCH -N 1\n")
                        if 'tasks' in resources:
                            script.write(f"#SBATCH --ntasks={resources['tasks']}\n")
                        if 'cores' in resources:
                            script.write(f"#SBATCH --cpus-per-task={resources['cores']}\n")
                        if 'time' in resources:
                            script.write(f"#SBATCH --time={resources['time']}\n")
                        if 'mem' in resources and (run.target.header_skip is None or '--mem' not in str(run.target.header_skip)):
                            script.write(f"#SBATCH --mem={resources['mem']}\n")
                        if run.target.queue is not None and run.target.queue != '':
                            script.write(f"#SBATCH --partition={run.target.gpu_queue if run.target.gpu else run.target.queue}\n")
                        if run.target.project is not None and run.target.project != '':
                            script.write(f"#SBATCH -A {run.target.project}\n")

                        script.write("#SBATCH --mail-type=END,FAIL\n")
                        script.write(f"#SBATCH --mail-user={run.user.email}\n")
                        script.write("#SBATCH --output=PlantIT.%j.out\n")
                        script.write("#SBATCH --error=PlantIT.%j.err\n")

                    callback_url = settings.API_URL + 'runs/' + run.identifier + '/status/'
                    script.write(run.target.pre_commands + '\n')

                    if 'input' in flow['config']:
                        sftp.mkdir(join(run.target.workdir, run.work_dir, 'input'))
                        pull_commands = f"plantit terrain pull {flow['config']['input']['from']} -p {join(run.target.workdir, run.work_dir, 'input')} {' '.join(['--pattern ' + pattern for pattern in flow['config']['input']['patterns']])} --plantit_url '{callback_url}' --plantit_token '{plantit_token}' --terrain_token {cyverse_token}\n"
                        script.write(pull_commands)
                        print(f"Using pull command: {pull_commands}")

                    run_commands = f"plantit run flow.yaml --plantit_url '{callback_url}' --plantit_token '{plantit_token}'"
                    docker_username = os.environ.get('DOCKER_USERNAME', None)
                    docker_password = os.environ.get('DOCKER_PASSWORD', None)
                    if docker_username is not None and docker_password is not None:
                        run_commands += f" --docker_username {docker_username} --docker_password {docker_password}"
                    run_commands += "\n"
                    script.write(run_commands)
                    print(f"Using run command: {run_commands}")

                    if 'output' in flow:
                        zip_commands = f"plantit zip {flow['output']['from']}"
                        if 'include' in flow['output']:
                            if 'patterns' in flow['output']['include']:
                                zip_commands = zip_commands + ' '.join(['--include_pattern ' + pattern for pattern in flow['output']['include']['patterns']])
                            if 'names' in flow['output']['include']:
                                zip_commands = zip_commands + ' '.join(['--include_name ' + pattern for pattern in flow['output']['include']['names']])
                            if 'patterns' in flow['output']['exclude']:
                                zip_commands = zip_commands + ' '.join(['--exclude_pattern ' + pattern for pattern in flow['output']['exclude']['patterns']])
                            if 'names' in flow['output']['exclude']:
                                zip_commands = zip_commands + ' '.join(['--exclude_name ' + pattern for pattern in flow['output']['exclude']['names']])
                        zip_commands += '\n'
                        print(f"Using zip command: {zip_commands}")

                        push_commands = f"plantit terrain push {flow['output']['to']} -p {join(run.workdir, flow['output']['from'])} --plantit_url '{callback_url}' --plantit_token '{plantit_token}' --terrain_token {cyverse_token}"
                        if 'include' in flow['output']:
                            if 'patterns' in flow['output']['include']:
                                push_commands = push_commands + ' '.join(['--include_pattern ' + pattern for pattern in flow['output']['include']['patterns']])
                            if 'names' in flow['output']['include']:
                                push_commands = push_commands + ' '.join(['--include_name ' + pattern for pattern in flow['output']['include']['names']])
                            if 'patterns' in flow['output']['exclude']:
                                push_commands = push_commands + ' '.join(['--exclude_pattern ' + pattern for pattern in flow['output']['exclude']['patterns']])
                            if 'names' in flow['output']['exclude']:
                                push_commands = push_commands + ' '.join(['--exclude_name ' + pattern for pattern in flow['output']['exclude']['names']])
                        push_commands += '\n'
                        script.write(push_commands)
                        print(f"Using push command: {push_commands}")

            pre_command = '; '.join(str(run.target.pre_commands).splitlines()) if run.target.pre_commands else ':'
            command = f"chmod +x {template_name} && ./{template_name}" if sandbox else f"chmod +x {template_name} && sbatch {template_name}"
            update_status(run, Status.CREATING, 'Running script' if sandbox else 'Submitting script to scheduler')
            execute_command(ssh_client=client, pre_command=pre_command, command=command, directory=work_dir)

            if run.status.state != 0:
                update_status(
                    run,
                    Status.COMPLETED if sandbox else Status.CREATING,
                    f"Run '{run.identifier}' {'completed' if sandbox else 'submitted'}")
            else:
                update_status(run, Status.FAILED, f"'{run.identifier}' failed")
            run.save()
    except SoftTimeLimitExceeded:
        update_status(run, Status.RUNNING, f"{run.identifier}' exceeded its walltime: {traceback.format_exc()}.")
        run.save()
        return
    except Exception:
        update_status(run, Status.FAILED, f"{run.identifier}' failed: {traceback.format_exc()}.")
        run.save()
