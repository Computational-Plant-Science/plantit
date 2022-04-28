import json
import logging

from asgiref.sync import async_to_sync, sync_to_async
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotFound

import plantit.queries as q
from plantit.github import get_repo, list_repo_branches
from plantit.users.models import Profile

logger = logging.getLogger(__name__)


def list_public(request):
    return JsonResponse({'workflows': q.list_public_workflows()})


@login_required
def list_user(request):
    profile = Profile.objects.get(user=request.user)
    return JsonResponse({'workflows': q.list_user_workflows(profile.github_username)})


@sync_to_async
@login_required
@async_to_sync
async def list_org(request):
    workflows = await q.list_user_org_workflows(request.user)
    return JsonResponse({'workflows': workflows})


@login_required
def list_project(request):
    return JsonResponse({'workflows': q.list_user_project_workflows(request.user)})


@sync_to_async
@login_required
@async_to_sync
async def get(request, owner, name, branch):
    profile = await sync_to_async(Profile.objects.get)(user=request.user)
    invalidate = request.GET.get('invalidate', False)
    workflow = await q.get_workflow(
        owner=owner,
        name=name,
        branch=branch,
        github_token=profile.github_token,
        cyverse_token=profile.cyverse_access_token,
        invalidate=bool(invalidate))

    # load the most recent submission config, if one exists
    last = q.get_last_task_config(request.user.username, owner, name, branch)
    if last is not None: workflow['last_config'] = last

    return HttpResponseNotFound() if workflow is None else JsonResponse(workflow)


@sync_to_async
@login_required
@async_to_sync
async def search(request, owner, name, branch):
    profile = await q.get_user_django_profile(request.user)
    repository = await get_repo(owner, name, branch, profile.github_token)
    return HttpResponseNotFound() if repository is None else JsonResponse(repository)


@sync_to_async
@login_required
@async_to_sync
async def refresh(request, owner, name, branch):
    try:
        profile = await q.get_user_django_profile(request.user)
        workflow = await q.get_workflow(owner, name, branch, profile.github_token, profile.cyverse_access_token)
    except: return HttpResponseNotFound()
    logger.info(f"Refreshed workflow {owner}/{name}/{branch}")
    return JsonResponse(workflow)


@sync_to_async
@login_required
@async_to_sync
async def branches(request, owner, name):
    profile = await q.get_user_django_profile(request.user)
    repo_branches = await list_repo_branches(owner, name, profile.github_token)
    return JsonResponse({'branches': [branch['name'] for branch in repo_branches]})
