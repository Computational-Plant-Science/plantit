import json
import os
import re
import traceback
from os.path import join

from datetime import datetime, timedelta

import requests
import yaml
from django.contrib.auth.models import User
from requests.auth import HTTPBasicAuth

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

    for line in iter(lambda: stdout.readline(2048), ""):
        print(f"Received stdout from '{ssh_client.host}': '{clean_html(line)}'")
    for line in iter(lambda: stderr.readline(2048), ""):
        print(f"Received stderr from '{ssh_client.host}': '{clean_html(line)}'")
    if stdout.channel.recv_exit_status():
        raise Exception(f"Received non-zero exit status from '{ssh_client.host}'")


def update_status(run: Run, state: int, description: str):
    print(description)
    run.status_set.create(description=description, state=state, location='PlantIT')
    run.save()


def __list_by_user(username, token):
    response = requests.get(
        f"https://api.github.com/search/code?q=filename:plantit.yaml+user:{username}",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
        })
    flows = [{
        'repo': item['repository'],
        'config': get_repo_config(item['repository']['name'], item['repository']['owner']['login'], token)
    } for item in response.json()['items']]

    return [flow for flow in flows if flow['config']['public']]


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


@app.task()
def execute(flow, run_id, plantit_token, cyverse_token):
    run = Run.objects.get(identifier=run_id)

    # if flow has outputs, make sure we don't push configuration or job scripts
    if 'output' in flow['config']:
        flow['config']['output']['exclude']['names'] = [
            "flow.yaml",
            "template_local_run.sh",
            "template_slurm_run.sh"]

    try:
        client = SSH(run.target.hostname, run.target.port, run.target.username)
        work_dir = join(run.target.workdir, run.work_dir)

        with client:
            update_status(run, Status.RUNNING, f"Creating working directory '{work_dir}'")
            execute_command(ssh_client=client,
                            pre_command=':',
                            command=f"mkdir {work_dir}",
                            directory=run.target.workdir)

            with client.client.open_sftp() as sftp:
                sftp.chdir(work_dir)

                update_status(run, Status.RUNNING, "Uploading configuration")
                # TODO refactor to allow multiple cluster schedulers
                sandbox = run.target.name == 'Sandbox'  # for now, we're either in the sandbox or on a SLURM cluster
                template = os.environ.get('CELERY_TEMPLATE_LOCAL_RUN_SCRIPT') if sandbox else os.environ.get('CELERY_TEMPLATE_SLURM_RUN_SCRIPT')
                template_name = template.split('/')[-1]

                with sftp.open('flow.yaml', 'w') as flow_file:
                    if 'resources' not in flow['config']['target']:
                        resources = None
                    else:
                        resources = flow['config']['target']['resources']
                    del flow['config']['target']

                    if not sandbox:
                        flow['config']['slurm'] = {
                            'cores': resources['cores'],
                            'processes': resources['tasks'],
                            'walltime': resources['time'],
                            'local_directory': work_dir,
                            'log_directory': work_dir,
                            'env_extra': [run.target.pre_commands]
                        }

                        if 'mem' in resources:
                            flow['config']['slurm']['memory'] = resources['mem']
                        if run.target.queue is not None and run.target.queue != '':
                            flow['config']['slurm']['queue'] = run.target.queue
                        if run.target.project is not None and run.target.project != '':
                            flow['config']['slurm']['project'] = run.target.project
                        if run.target.header_skip is not None and run.target.header_skip != '':
                            flow['config']['slurm']['header_skip'] = run.target.header_skip.split(',')

                    if 'gpu' in flow['config']:
                        if run.target.gpu:
                            flow['config']['slurm']['extra'] = [f"--gres=gpu:{resources['cores']}"]
                            flow['config']['slurm']['queue'] = run.target.gpu_queue
                        else:
                            update_status(run, Status.RUNNING, f"No GPU support on {run.target.name}")

                    yaml.dump(flow['config'], flow_file, default_flow_style=False)

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

                    script.write(run.target.pre_commands + '\n')
                    commands = f"plantit flow.yaml --plantit_token '{plantit_token}' --cyverse_token '{cyverse_token}'"
                    docker_username = os.environ.get('DOCKER_USERNAME', None)
                    docker_password = os.environ.get('DOCKER_PASSWORD', None)
                    if docker_username is not None and docker_password is not None:
                        commands += f" --docker_username {docker_username} --docker_password {docker_password}"
                    commands += "\n"
                    script.write(commands)
                    print(f"Using PlantIT command: {commands}")

            pre_command = '; '.join(str(run.target.pre_commands).splitlines()) if run.target.pre_commands else ':'
            command = f"chmod +x {template_name} && ./{template_name}" if sandbox else f"chmod +x {template_name} && sbatch {template_name}"
            update_status(run, Status.RUNNING, 'Starting' if sandbox else 'Submitting')
            execute_command(ssh_client=client, pre_command=pre_command, command=command, directory=work_dir)

            if run.status.state != 2:
                update_status(
                    run,
                    Status.COMPLETED if sandbox else Status.RUNNING,
                    f"'{run.identifier}' {'completed' if sandbox else 'submitted'}")
            else:
                update_status(run, Status.FAILED, f"'{run.identifier}' failed")
            run.save()
    except Exception:
        update_status(run, Status.FAILED, f"{run.identifier}' failed: {traceback.format_exc()}.")
        run.save()
