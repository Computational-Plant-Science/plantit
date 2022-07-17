import json
import logging
from typing import List, Dict

from asgiref.sync import async_to_sync, sync_to_async
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseNotFound
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

from plantit.cache import list_org_workflows, list_public_workflows, list_user_workflows, get_user_github_organizations, get_workflow_async
from plantit.filters import list_user_project_workflows, list_user_org_workflows
from plantit.github import AsyncGitHubClient
from plantit.redis import RedisClient
from plantit.users.models import Profile

logger = logging.getLogger(__name__)


# Utilities

@sync_to_async
def get_user_django_profile_async(user: User):
    profile = Profile.objects.get(user=user)
    return profile


def get_last_task_config(username, owner, name, branch):
    redis = RedisClient.get()
    last_config = redis.get(f"workflow_configs/{username}/{owner}/{name}/{branch}")
    return None if last_config is None else json.loads(last_config)


# Views

@swagger_auto_schema(methods='get')
@api_view(['get'])
def list_public(request):
    return JsonResponse({'workflows': list_public_workflows()})


@login_required
def list_user(request):
    profile = Profile.objects.get(user=request.user)
    return JsonResponse({'workflows': list_user_workflows(profile.github_username)})


@login_required
def list_org(request):
    workflows = list_user_org_workflows(request.user)
    return JsonResponse({'workflows': workflows})


@login_required
def list_project(request):
    return JsonResponse({'workflows': list_user_project_workflows(request.user)})


@sync_to_async
@login_required
@async_to_sync
async def get(request, owner, name, branch):
    profile = await sync_to_async(Profile.objects.get)(user=request.user)
    invalidate = request.GET.get('invalidate', False)
    workflow = await get_workflow_async(
        owner=owner,
        name=name,
        branch=branch,
        github_token=profile.github_token,
        invalidate=bool(invalidate))

    # load the most recent submission config, if one exists
    last_config = get_last_task_config(request.user.username, owner, name, branch)
    if last_config is not None: workflow['last_config'] = last_config
    return HttpResponseNotFound() if workflow is None else JsonResponse(workflow)


@sync_to_async
@login_required
@async_to_sync
async def search(request, owner, name, branch):
    profile = await get_user_django_profile_async(request.user)
    github = AsyncGitHubClient(access_token=profile.github_token)
    repository = await github.get_repo_async(owner, name, branch)
    return HttpResponseNotFound() if repository is None else JsonResponse(repository)


@sync_to_async
@login_required
@async_to_sync
async def refresh(request, owner, name, branch):
    try:
        profile = await get_user_django_profile_async(request.user)
        workflow = await get_workflow_async(owner=owner,
                                            name=name,
                                            branch=branch,
                                            github_token=profile.github_token)
    except: return HttpResponseNotFound()
    logger.info(f"Refreshed workflow {owner}/{name}/{branch}")
    return JsonResponse(workflow)


@sync_to_async
@login_required
@async_to_sync
async def branches(request, owner, name):
    profile = await get_user_django_profile_async(request.user)
    github = AsyncGitHubClient(access_token=profile.github_token)
    repo_branches = await github.list_repo_branches_async(owner, name)
    return JsonResponse({'branches': [branch['name'] for branch in repo_branches]})
