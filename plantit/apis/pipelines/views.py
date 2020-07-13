import binascii
import os
import traceback
import uuid
from os.path import join

import requests
import yaml
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.decorators import api_view

from apis.util import get_config
from plantit.celery import app
from plantit.runs.models.cluster import Cluster
from plantit.runs.models.run import Run
from plantit.runs.models.status import Status
from plantit.runs.ssh import SSH

import re


def clean_html(raw_html):
    expr = re.compile('<.*?>')
    text = re.sub(expr, '', raw_html)
    return text


def execute_command(run: Run, ssh_client: SSH, pre_command: str, command: str, directory: str):
    cmd = f"cd {directory}; {pre_command}; {command}" if directory else command
    print(f"Executing remote command: '{cmd}'")
    stdin, stdout, stderr = ssh_client.client.exec_command(cmd)
    stdin.close()
    for line in iter(lambda: stdout.readline(2048), ""):
        print(f"Received stout from remote command: '{clean_html(line)}'")
    for line in iter(lambda: stderr.readline(2048), ""):
        print(f"Received sterr from remote command: '{clean_html(line)}'")

    if stdout.channel.recv_exit_status():
        raise Exception(f"Received non-zero exit status from remote command")
    else:
        print(f"Successfully executed remote command.")


@app.task()
def execute(workflow, run_id, token):
    run = Run.objects.get(identifier=run_id)
    run.status_set.create(description=f"Run started.",
                          state=Status.RUNNING,
                          location='PlantIT')
    run.save()

    try:
        work_dir = join(run.cluster.workdir, run.work_dir)
        ssh_client = SSH(run.cluster.hostname,
                         run.cluster.port,
                         run.cluster.username,
                         run.cluster.password) if run.cluster.password else SSH(run.cluster.hostname,
                                                                                run.cluster.port,
                                                                                run.cluster.username)

        with ssh_client:
            execute_command(run=run, ssh_client=ssh_client, pre_command=':', command=f"mkdir {work_dir}",
                            directory=run.cluster.workdir)
            print(f"Created working directory '{work_dir}'. Uploading workflow definition...")
            run.status_set.create(
                description=f"Created working directory. Uploading workflow definition...",
                state=Status.RUNNING,
                location='PlantIT')
            run.save()

            with ssh_client.client.open_sftp() as sftp:
                sftp.chdir(work_dir)
                with sftp.open('workflow.yaml', 'w') as file:
                    yaml.dump(workflow['config'], file, default_flow_style=False)
            print(f"Uploaded workflow definition to '{work_dir}'. Running workflow...")
            run.status_set.create(
                description=f"Uploaded workflow definition. Running workflow...",
                state=Status.RUNNING,
                location='PlantIT')
            run.save()

            execute_command(run=run, ssh_client=ssh_client, pre_command='; '.join(
                str(run.cluster.pre_commands).splitlines()) if run.cluster.pre_commands else ':',
                            command=f"plantit workflow.yaml --token {token}",
                            directory=work_dir)
            print(f"Run completed.")
            run.status_set.create(
                description=f"Run completed.",
                state=Status.COMPLETED,
                location='PlantIT')
            run.save()

    except Exception:
        run.status_set.create(
            description=f"Run failed: {traceback.format_exc()}.",
            state=Status.FAILED,
            location='PlantIT')
        run.save()


@login_required
def list(request):
    token = request.user.profile.github_auth_token
    response = requests.get(
        f"https://api.github.com/search/code?q=filename:plantit.yaml+org:computational-plant-science") if '' == token \
        else requests.get(f"https://api.github.com/search/code?q=filename:plantit.yaml+org:computational-plant-science",
                          headers={"Authorization": f"token {token}"})

    return JsonResponse({
        'pipelines': [{
            'repo': item['repository'],
            'config': get_config(item['repository'], token)
        } for item in response.json()['items']]
    })


@login_required
def get(request, owner, name):
    token = request.user.profile.github_auth_token
    repo = requests.get(f"https://api.github.com/repos/{owner}/{name}",
                        headers={"Authorization": f"token {token}"}).json()
    config = get_config(repo, token)
    return JsonResponse({
        'repo': repo,
        'config': config
    })


def get_executor(cluster):
    return {
        'in-process': {}
    }


@login_required
@api_view(['POST'])
def start(request):
    user = request.user
    workflow = request.data

    now = timezone.now()
    now_str = now.strftime('%s')

    cluster = Cluster.objects.get(name=workflow['config']['target']['name'])
    run = Run.objects.create(
        user=User.objects.get(username=user.username),
        workflow_owner=workflow['repo']['owner']['login'],
        workflow_name=workflow['repo']['name'],
        cluster=cluster,
        created=now,
        work_dir=now_str + "/",
        remote_results_path=now_str + "/",
        identifier=uuid.uuid4(),
        token=binascii.hexlify(os.urandom(20)).decode())
    workflow_path = f"{workflow['repo']['owner']['login']}/{workflow['repo']['name']}"
    run.status_set.create(description=f"Workflow '{workflow_path}' run '{run.identifier}' created.",
                          state=Status.CREATED,
                          location='PlantIT')
    run.save()

    # token = request.session._session['csrfToken']
    token = run.token
    config = {
        'identifier': run.identifier,
        'api_url': os.environ['DJANGO_API_URL'] + f"runs/{run.identifier}/update_status/",
        'workdir': join(cluster.workdir, now_str),
        'clone': f"https://github.com/{workflow_path}" if workflow['config']['clone'] else None,
        'image': workflow['config']['image'],
        'command': workflow['config']['commands'],
        'params': workflow['config']['params'],
        'executor': get_executor(cluster)
    }
    if 'input' in workflow['config']:
        config['input'] = workflow['config']['input']
    if 'output' in workflow['config']:
        config['output'] = workflow['config']['output']

    execute.delay({
        'repo': workflow['repo'],
        'config': config
    }, run.identifier, token)

    return JsonResponse({
        'id': run.identifier
    })
