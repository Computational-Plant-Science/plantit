import django
import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone, dateparse
from rest_framework.decorators import api_view

from apis.util import get_config


from os.path import join

from dagster import DagsterEventType, execute_pipeline_iterator

from plantit.celery import app
from plantit.runs.dagster.pipelines import plantit_pipeline
from plantit.runs.models.cluster import Cluster
from plantit.runs.models.run import Run
from plantit.runs.models.status import Status


@app.task()
def run_pipeline(pipeline, run_id):
    run = Run.objects.get(submission_id=run_id)
    del pipeline['target']
    run.status_set.create(description="Created")
    for event in execute_pipeline_iterator(
            plantit_pipeline,
            run_config={
                'solids': {
                    'create_working_directory': {
                        'command': f"mkdir {run.work_dir}",
                        'directory': run.cluster.workdir
                    },
                    'upload_pipeline': {
                        'pipeline': pipeline,
                        'directory': run.work_dir
                    },
                    'execute_command': {
                        'command': f"plantit run pipeline.yaml",
                        'directory': run.work_dir
                    }
                },
                'resources': {
                    'ssh': {
                        'config': {
                            'host': run.cluster.hostname,
                            'port': run.cluster.port,
                            'username': run.cluster.username,
                        }
                    }
                },
                "execution": {
                    "celery": {
                        "config": {
                            "backend": "amqp://rabbitmq",
                            "broker": "amqp://rabbitmq"
                        }
                    }
                },
                'storage': {
                    'filesystem': {
                        'config': {
                            'base_dir': '/opt/dagster'
                        }
                    }
                },
                'loggers': {
                    'console': {
                        'config': {
                            'log_level': 'INFO'
                        }
                    }
                }
            }):
        print(f"Dagster event '{event.event_type}' with message '{event.message}'")
        if event.event_type is DagsterEventType.PIPELINE_INIT_FAILURE or event.is_pipeline_failure:
            run.status_set.create(state=Status.FAILED, description=event.message)
            raise Exception(event.message)
        run.status_set.create(state=Status.OK, description=event.message)
    run.status_set.create(state=Status.OK, description=f"Completed")


@login_required
def list(request):
    token = request.user.profile.github_auth_token
    response = requests.get(
        f"https://api.github.com/search/code?q=filename:plantit.yaml+org:computational-plant-science",
        headers={"Authorization": f"token {token}"}
    )
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


@login_required
@api_view(['POST'])
def start(request):
    user = request.user
    pipeline = request.data

    now = timezone.now()
    now_str = now.strftime('%s')

    cluster = Cluster.objects.get(name=pipeline['config']['target']['name'])
    run = Run.objects.create(
        user=User.objects.get(username=user.username),
        pipeline_owner=pipeline['repo']['owner']['login'],
        pipeline_name=pipeline['repo']['name'],
        cluster=cluster,
        created=now,
        submission_id=now_str,
        work_dir=now_str + "/",
        remote_results_path=now_str + "/")
    run.save()

    run_pipeline.delay(pipeline, run.submission_id)

    return JsonResponse({
        'id': run.submission_id
    })
