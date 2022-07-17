import logging

from asgiref.sync import async_to_sync, sync_to_async
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotFound
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

import plantit.queries as q
from plantit.github import AsyncGitHubClient
from plantit.users.models import Profile

logger = logging.getLogger(__name__)


@swagger_auto_schema(methods='get')
@api_view(['get'])
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
    workflows = await q.list_user_org_workflows_async(request.user)
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
    workflow = await q.get_workflow_async(
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
    profile = await q.get_user_django_profile_async(request.user)
    github = AsyncGitHubClient(access_token=profile.github_token)
    repository = await github.get_repo_async(owner, name, branch)
    return HttpResponseNotFound() if repository is None else JsonResponse(repository)


@sync_to_async
@login_required
@async_to_sync
async def refresh(request, owner, name, branch):
    try:
        profile = await q.get_user_django_profile_async(request.user)
        workflow = await q.get_workflow_async(owner=owner,
                                              name=name,
                                              branch=branch,
                                              github_token=profile.github_token,
                                              cyverse_token=profile.cyverse_access_token)
    except: return HttpResponseNotFound()
    logger.info(f"Refreshed workflow {owner}/{name}/{branch}")
    return JsonResponse(workflow)


@sync_to_async
@login_required
@async_to_sync
async def branches(request, owner, name):
    profile = await q.get_user_django_profile_async(request.user)
    github = AsyncGitHubClient(access_token=profile.github_token)
    repo_branches = await github.list_repo_branches_async(owner, name)
    return JsonResponse({'branches': [branch['name'] for branch in repo_branches]})
