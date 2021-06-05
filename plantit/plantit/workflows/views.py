import json
import logging
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseNotAllowed, HttpResponse
from rest_framework.decorators import api_view

from plantit.github import get_repo_readme, get_repo, list_connectable_repos_by_owner
from plantit.redis import RedisClient
from plantit.celery_tasks import refresh_all_workflows, refresh_personal_workflows
from plantit.users.models import Profile
from plantit.workflows.models import Workflow
from plantit.workflows.utils import map_workflow, rescan_public_workflows, rescan_personal_workflows

logger = logging.getLogger(__name__)


@api_view(['GET'])
@login_required
def list_public(request):
    redis = RedisClient.get()

    debounce = request.GET.get('debounce', None)
    if debounce is None or debounce == 'True':  # only invalidate and refresh the cache if it's old
        updated = redis.get('public_workflows_updated')
        if updated is None:
            # refresh_all_workflows.delay(token=request.user.profile.github_token)
            rescan_public_workflows(request.user.profile.github_token)
        else:
            age = (datetime.now() - datetime.fromtimestamp(float(updated)))
            if age.total_seconds() > (int(settings.WORKFLOWS_REFRESH_MINUTES) * 60):
                logger.info(f"Public workflow cache age is {age}, refreshing")
                # refresh_all_workflows.delay(token=request.user.profile.github_token)
                rescan_public_workflows(request.user.profile.github_token)
            else:
                logger.info(f"Public workflow cache age is {age}, still fresh")
    else:  # force inval/refresh
        rescan_public_workflows(request.user.profile.github_token)

    workflows = [json.loads(redis.get(key)) for key in redis.scan_iter(match='workflows/*')]
    workflows = [workflow for workflow in workflows if workflow['public']]
    return JsonResponse({'workflows': workflows})


@api_view(['GET'])
@login_required
def list_personal(request, owner):
    if owner != request.user.profile.github_username:
        try:
            Profile.objects.get(github_username=owner)
        except:
            return HttpResponseNotFound()

    redis = RedisClient.get()

    debounce = request.GET.get('debounce', None)
    if debounce is None or debounce == 'True':  # only invalidate and refresh the cache if it's stale
        updated = redis.get(f"workflows_updated/{owner}")
        if updated is None:
            # refresh_personal_workflows.delay(owner=owner)
            rescan_personal_workflows(owner)
        else:
            age = (datetime.now() - datetime.fromtimestamp(float(updated)))
            if age.total_seconds() > (int(settings.WORKFLOWS_REFRESH_MINUTES) * 60):
                logger.info(f"{owner}'s workflow cache age is {age}, refreshing")
                rescan_personal_workflows(owner)
            else:
                logger.info(f"{owner}'s workflow cache age is {age}, still fresh")
    else:  # force inval/refresh
        rescan_personal_workflows(owner)

    return JsonResponse({'workflows': [json.loads(redis.get(key)) for key in redis.scan_iter(match=f"workflows/{owner}/*")]})


@api_view(['GET'])
@login_required
def get(request, owner, name):
    redis = RedisClient.get()
    workflow = redis.get(f"workflows/{owner}/{name}")
    return HttpResponseNotFound() if workflow is None else JsonResponse(json.loads(workflow))


@api_view(['GET'])
@login_required
def search(request, owner, name):
    repo = get_repo(owner, name, request.user.profile.github_token)
    return HttpResponseNotFound() if repo is None else JsonResponse(repo)


@api_view(['GET'])
@login_required
def refresh(request, owner, name):
    try:
        workflow = Workflow.objects.get(repo_owner=owner, repo_name=name)
    except:
        return HttpResponseNotFound()

    redis = RedisClient.get()
    repo = get_repo(workflow.repo_owner, workflow.repo_name, request.user.profile.github_token)
    repo['public'] = workflow.public
    redis.set(f"workflows/{owner}/{name}", json.dumps(repo))
    return JsonResponse(repo)


@api_view(['GET'])
@login_required
def readme(request, owner, name):
    return JsonResponse({'readme': get_repo_readme(name, owner, request.user.profile.github_token)})


@api_view(['POST'])
@login_required
def connect(request, owner, name):
    if owner != request.user.profile.github_username:
        return HttpResponseNotAllowed()

    redis = RedisClient.get()
    redis.set(f"workflows/{owner}/{name}", json.dumps(request.data))
    workflow, created = Workflow.objects.get_or_create(user=request.user, repo_owner=owner, repo_name=name, public=False)
    if created:
        async_to_sync(get_channel_layer().group_send)(f"workflows-{owner}", {
            'type': 'update_workflow',
            'workflow': map_workflow(workflow, request.user.profile.github_token)
        })

    if created:
        logger.info(f"Connected repository {owner}/{name} as {request.data['config']['name']} for {request.user.username}")
        return JsonResponse({'connected': True})
    else:
        logger.info(f"Repository {owner}/{name} already connected as {request.data['config']['name']} for {request.user.username}")
        return JsonResponse({'connected': False})


@api_view(['DELETE'])
@login_required
def disconnect(request, owner, name):
    if owner != request.user.profile.github_username:
        return HttpResponseNotAllowed()

    try:
        workflow = Workflow.objects.get(user=request.user, repo_owner=owner, repo_name=name)
    except:
        return HttpResponseNotFound()

    workflow.delete()

    redis = RedisClient.get()
    redis.delete(f"workflows/{owner}/{name}")
    return HttpResponse()
