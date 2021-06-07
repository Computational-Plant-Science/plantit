import json
import logging

from asgiref.sync import async_to_sync, sync_to_async
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseForbidden
from rest_framework.decorators import api_view

from plantit.github import get_repo_readme, get_repo
from plantit.redis import RedisClient
from plantit.users.models import Profile
from plantit.workflows.models import Workflow
from plantit.workflows.utils import bind_workflow, get_personal_workflows, get_public_workflows, get_workflow

logger = logging.getLogger(__name__)

# TODO: when this (https://code.djangoproject.com/ticket/31949) gets merged, remove the sync_to_async/async_to_sync hack


@sync_to_async
@login_required
@async_to_sync
async def list_public(request):
    invalidate = request.GET.get('invalidate', False)
    workflows = await get_public_workflows(invalidate=bool(invalidate))
    return JsonResponse({'workflows': workflows})


@sync_to_async
@login_required
@async_to_sync
async def list_personal(request, owner):
    if owner != request.user.profile.github_username:
        try:
            Profile.objects.get(github_username=owner)
        except:
            return HttpResponseNotFound()

    invalidate = request.GET.get('invalidate', False)
    workflows = await get_personal_workflows(owner=owner, invalidate=bool(invalidate))
    return JsonResponse({'workflows': workflows})


@sync_to_async
@login_required
@async_to_sync
async def get(request, owner, name):
    invalidate = request.GET.get('invalidate', False)
    workflow = await get_workflow(owner=owner, name=name, token=request.user.profile.github_token, invalidate=bool(invalidate))
    return HttpResponseNotFound() if workflow is None else JsonResponse(workflow)


@sync_to_async
@login_required
@async_to_sync
async def search(request, owner, name):
    repo = await get_repo(owner, name, request.user.profile.github_token)
    return HttpResponseNotFound() if repo is None else JsonResponse(repo)


@sync_to_async
@login_required
@async_to_sync
async def refresh(request, owner, name):
    try:
        workflow = Workflow.objects.get(repo_owner=owner, repo_name=name)
    except:
        return HttpResponseNotFound()

    redis = RedisClient.get()
    bound = await bind_workflow(workflow, request.user.profile.github_token)
    redis.set(f"workflows/{owner}/{name}", json.dumps(bound))
    logger.info(f"Refreshed workflow {owner}/{name}")
    return JsonResponse(bound)


@sync_to_async
@login_required
@async_to_sync
def readme(request, owner, name):
    rm = get_repo_readme(name, owner, request.user.profile.github_token)
    return JsonResponse({'readme': rm})


@sync_to_async
@login_required
@async_to_sync
def connect(request, owner, name):
    if owner != request.user.profile.github_username:
        return HttpResponseForbidden()

    redis = RedisClient.get()
    request.data['connected'] = True
    redis.set(f"workflows/{owner}/{name}", json.dumps(request.data))
    Workflow.objects.create(user=request.user, repo_owner=owner, repo_name=name, public=False)
    logger.info(f"Connected workflow {owner}/{name} as {request.data['config']['name']}")
    return JsonResponse({'workflows': [json.loads(redis.get(key)) for key in redis.scan_iter(match=f"workflows/{owner}/*")]})


@sync_to_async
@login_required
@async_to_sync
async def toggle_public(request, owner, name):
    if owner != request.user.profile.github_username:
        return HttpResponseForbidden()

    try:
        workflow = Workflow.objects.get(user=request.user, repo_owner=owner, repo_name=name)
    except:
        return HttpResponseNotFound()

    redis = RedisClient.get()
    workflow.public = not workflow.public
    workflow.save()
    bound = await bind_workflow(workflow, request.user.profile.github_token)
    redis.set(f"workflows/{owner}/{name}", json.dumps(bound))
    logger.info(f"Workflow {owner}/{name} is now {'public' if workflow.public else 'private'}")
    return JsonResponse({'workflows': [json.loads(redis.get(key)) for key in redis.scan_iter(match=f"workflows/{owner}/*")]})


@sync_to_async
@login_required
@async_to_sync
def disconnect(request, owner, name):
    if owner != request.user.profile.github_username:
        return HttpResponseForbidden()

    try:
        workflow = Workflow.objects.get(user=request.user, repo_owner=owner, repo_name=name)
    except:
        return HttpResponseNotFound()

    workflow.delete()
    redis = RedisClient.get()
    cached = json.loads(redis.get(f"workflows/{owner}/{name}"))
    cached['public'] = False
    cached['connected'] = False
    redis.set(f"workflows/{owner}/{name}", json.dumps(cached))
    logger.info(f"Disconnected workflow {owner}/{name}")
    return JsonResponse({'workflows': [json.loads(redis.get(key)) for key in redis.scan_iter(match=f"workflows/{owner}/*")]})
