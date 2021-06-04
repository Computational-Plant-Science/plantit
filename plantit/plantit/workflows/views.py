import json
import logging
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseNotAllowed, HttpResponse
from rest_framework.decorators import api_view

from plantit.github import get_repo_readme, get_repo
from plantit.redis import RedisClient
from plantit.celery_tasks import refresh_all_workflows, refresh_personal_workflows
from plantit.users.models import Profile
from plantit.workflows.models import Workflow

logger = logging.getLogger(__name__)


@login_required
def list_public(request):
    redis = RedisClient.get()
    updated = redis.get('public_workflows_updated')

    if updated is None:
        refresh_all_workflows.delay(token=request.user.profile.github_token)
    else:
        seconds_since_refresh = (datetime.now() - datetime.fromtimestamp(float(updated)))
        if seconds_since_refresh.total_seconds() > (int(settings.WORKFLOWS_REFRESH_MINUTES) * 60):
            refresh_all_workflows.delay(token=request.user.profile.github_token)

    workflows = [json.loads(redis.get(key)) for key in redis.scan_iter(match='workflows/*')]
    workflows = [workflow for workflow in workflows if workflow['public']]
    return JsonResponse({'workflows': workflows})


@login_required
def list_personal(request, owner):
    if owner != request.user.profile.github_username:
        try:
            Profile.objects.get(github_username=owner)
        except:
            return HttpResponseNotFound()

    # TODO debounce this- shouldn't allow refresh e.g. multiple times a second, max every few seconds is probably ideal
    refresh_personal_workflows.delay(owner=owner)

    redis = RedisClient.get()
    workflows = [json.loads(redis.get(key)) for key in redis.scan_iter(match=f"workflows/{owner}/*")]

    name = request.GET.get('name', None)
    if name is not None:
        workflows = [workflow for workflow in workflows if name in workflow['config']['name']]

    return JsonResponse({'workflows': workflows})


@login_required
def get(request, owner, name):
    redis = RedisClient.get()
    workflow = redis.get(f"workflows/{owner}/{name}")
    return HttpResponseNotFound() if workflow is None else JsonResponse(json.loads(workflow))


@login_required
def search(request, owner, name):
    repo = get_repo(owner, name, request.user.profile.github_token)
    return HttpResponseNotFound() if repo is None else JsonResponse(repo)


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
