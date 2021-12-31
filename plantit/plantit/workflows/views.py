import json
import logging

import traceback
from asgiref.sync import async_to_sync, sync_to_async
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotFound

from plantit.github import get_repo_readme, get_repo, list_repo_branches, list_user_organizations
from plantit.redis import RedisClient
from plantit.utils import get_user_django_profile, list_public_workflows, refresh_org_workflow_cache, get_workflow, \
    check_user_authentication, list_user_projects, refresh_project_cache
from plantit.users.models import Profile
from plantit.miappe.models import Investigation
from plantit.celery_tasks import refresh_user_workflows

logger = logging.getLogger(__name__)


def list_public(request):
    return JsonResponse({'workflows': list_public_workflows()})


# TODO: when this (https://code.djangoproject.com/ticket/31949) gets merged, remove sync_to_async/async_to_sync hacks
@sync_to_async
@login_required
@async_to_sync
async def list_user(request):
    profile = await sync_to_async(Profile.objects.get)(user=request.user)

    # if user's workflow cache is empty (re)populate it
    redis = RedisClient.get()
    last_updated = redis.get(f"workflows_updated/{profile.github_username}")
    num_cached = len(list(redis.scan_iter(match=f"workflows/{profile.github_username}/*")))
    if last_updated is None or num_cached == 0:
        logger.info(f"{profile.github_username}'s workflow cache is empty, populating it now")
        refresh_user_workflows.s(profile.github_username).apply_async()

    workflows = [json.loads(redis.get(key)) for key in redis.scan_iter(match=f"workflows/{profile.github_username}/*")]
    return JsonResponse({'workflows': workflows})


@sync_to_async
@login_required
@async_to_sync
async def list_org(request):
    profile = await get_user_django_profile(request.user)

    # TODO cache organization memberships so don't have to look up each time
    orgs = await list_user_organizations(profile.github_username, profile.github_token)
    redis = RedisClient.get()
    wfs = dict()

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
        wfs[org_name] = workflows

    return JsonResponse({'workflows': wfs})


@sync_to_async
@login_required
@async_to_sync
async def list_project(request):
    # TODO cache organization memberships so don't have to look up each time
    projects = await list_user_projects(request.user)
    redis = RedisClient.get()
    wfs = dict()

    # load workflows for each project
    for proj in projects:
        cached = redis.get(f"projects/{proj.unique_id}")
        if cached is None: refresh_project_cache(proj)

        keys = json.loads(redis.get(f"projects/{proj.unique_id}"))['workflows']
        workflows = [json.loads(redis.get(key)) for key in [f"workflows/{k}" for k in keys]]
        wfs[proj.unique_id] = workflows

    return JsonResponse({'workflows': wfs})


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
    except:
        return HttpResponseNotFound()

    logger.info(f"Refreshed workflow {owner}/{name}/{branch}")
    from pprint import pprint
    pprint(workflow)
    return JsonResponse(workflow)


@login_required
def readme(request, owner, name):
    rm = get_repo_readme(name, owner, request.user.profile.github_token)
    return JsonResponse({'readme': rm})


@sync_to_async
@login_required
@async_to_sync
async def branches(request, owner, name):
    profile = await get_user_django_profile(request.user)
    bs = await list_repo_branches(owner, name, profile.github_token)
    return JsonResponse({'branches': [b['name'] for b in bs]})
