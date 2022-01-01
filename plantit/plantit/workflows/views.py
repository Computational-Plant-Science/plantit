import json
import logging

from asgiref.sync import async_to_sync, sync_to_async
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotFound

from plantit.celery_tasks import refresh_user_workflows
from plantit.github import get_repo_readme, get_repo, list_repo_branches, list_user_organizations
from plantit.redis import RedisClient
from plantit.users.models import Profile
from plantit.utils import get_user_django_profile, list_public_workflows, refresh_org_workflow_cache, get_workflow, \
    list_user_projects, project_to_dict

logger = logging.getLogger(__name__)


def list_public(request):
    return JsonResponse({'workflows': list_public_workflows()})


# TODO: when this (https://code.djangoproject.com/ticket/31949) gets merged, remove sync_to_async/async_to_sync hacks
@sync_to_async
@login_required
@async_to_sync
async def list_user(request):
    profile = await sync_to_async(Profile.objects.get)(user=request.user)
    redis = RedisClient.get()
    last_updated = redis.get(f"workflows_updated/{profile.github_username}")
    num_cached = len(list(redis.scan_iter(match=f"workflows/{profile.github_username}/*")))

    # if user's workflow cache is empty (re)populate it
    if last_updated is None or num_cached == 0:
        logger.info(f"{profile.github_username}'s workflow cache is empty, populating it now")
        refresh_user_workflows.s(profile.github_username).apply_async()

    workflows = [json.loads(redis.get(key)) for key in redis.scan_iter(match=f"workflows/{profile.github_username}/*")]
    return JsonResponse({'workflows': workflows})


@sync_to_async
@login_required
@async_to_sync
async def list_org(request):
    # TODO cache organization memberships so don't have to look up each time
    profile = await get_user_django_profile(request.user)
    orgs = await list_user_organizations(profile.github_username, profile.github_token)
    redis = RedisClient.get()
    org_workflows = dict()

    # load workflows for each org
    for org in orgs:
        org_name = org['login']
        last_updated = redis.get(f"workflows_updated/{org_name}")
        num_cached = len(list(redis.scan_iter(match=f"workflows/{org_name}/*")))

        # if org's workflow cache is empty, (re)populate it before returning
        if last_updated is None or num_cached == 0:
            logger.info(f"GitHub organization {org_name}'s workflow cache is empty, populating it now")
            await refresh_org_workflow_cache(org_name, profile.github_token)

        workflows = [json.loads(redis.get(key)) for key in redis.scan_iter(match=f"workflows/{org_name}/*")]
        org_workflows[org_name] = workflows

    return JsonResponse({'workflows': org_workflows})


@sync_to_async
@login_required
@async_to_sync
async def list_project(request):
    redis = RedisClient.get()
    project_workflows = dict()

    # load workflows for each project
    for project in (await list_user_projects(request.user)):
        proj_dict = await sync_to_async(project_to_dict)(project)
        workflows = [json.loads(wf) for wf in [redis.get(key) for key in [f"workflows/{name}" for name in proj_dict['workflows']]] if wf is not None]
        project_workflows[project.guid] = workflows

    return JsonResponse({'workflows': project_workflows})


@sync_to_async
@login_required
@async_to_sync
async def get(request, owner, name, branch):
    profile = await sync_to_async(Profile.objects.get)(user=request.user)
    invalidate = request.GET.get('invalidate', False)
    workflow = await get_workflow(
        owner=owner,
        name=name,
        branch=branch,
        github_token=profile.github_token,
        cyverse_token=profile.cyverse_access_token,
        invalidate=bool(invalidate))

    # load the most recent submission config, if one exists
    redis = RedisClient.get()
    last_config = redis.get(f"workflow_configs/{request.user.username}/{owner}/{name}/{branch}")
    if last_config is not None: workflow['last_config'] = json.loads(last_config)

    return HttpResponseNotFound() if workflow is None else JsonResponse(workflow)


@sync_to_async
@login_required
@async_to_sync
async def search(request, owner, name, branch):
    profile = await get_user_django_profile(request.user)
    repository = await get_repo(owner, name, branch, profile.github_token)
    return HttpResponseNotFound() if repository is None else JsonResponse(repository)


@sync_to_async
@login_required
@async_to_sync
async def refresh(request, owner, name, branch):
    try:
        profile = await get_user_django_profile(request.user)
        workflow = await get_workflow(owner, name, branch, profile.github_token, profile.cyverse_access_token)
    except: return HttpResponseNotFound()
    logger.info(f"Refreshed workflow {owner}/{name}/{branch}")
    return JsonResponse(workflow)


@login_required
def readme(request, owner, name):
    return JsonResponse({'readme': get_repo_readme(name, owner, request.user.profile.github_token)})


@sync_to_async
@login_required
@async_to_sync
async def branches(request, owner, name):
    profile = await get_user_django_profile(request.user)
    repo_branches = await list_repo_branches(owner, name, profile.github_token)
    return JsonResponse({'branches': [branch['name'] for branch in repo_branches]})
