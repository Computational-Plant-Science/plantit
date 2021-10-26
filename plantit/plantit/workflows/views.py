import json
import logging

from asgiref.sync import async_to_sync, sync_to_async
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseForbidden

from plantit.github import get_repo_readme, get_repo, list_repo_branches
from plantit.redis import RedisClient
from plantit.utils import get_user_django_profile, list_public_workflows, list_personal_workflows, get_workflow, \
    workflow_to_dict, check_user_authentication
from plantit.misc import del_none
from plantit.users.models import Profile
from plantit.workflows.models import Workflow
from plantit.celery_tasks import refresh_personal_workflows

logger = logging.getLogger(__name__)

# TODO: when this (https://code.djangoproject.com/ticket/31949) gets merged, remove the sync_to_async/async_to_sync hack


async def list_public(request):
    if await check_user_authentication(request.user):
        profile = await get_user_django_profile(request.user)
        github_token = profile.github_token
        cyverse_token = profile.cyverse_access_token
    else:
        github_token = None
        cyverse_token = None

    invalidate = request.GET.get('invalidate', False)
    workflows = await list_public_workflows(github_token=github_token, cyverse_token=cyverse_token, invalidate=invalidate)
    return JsonResponse({'workflows': workflows})


@sync_to_async
@login_required
@async_to_sync
async def list_personal(request, owner):
    profile = await sync_to_async(Profile.objects.get)(user=request.user)
    if owner != profile.github_username:
        try:
            await sync_to_async(Profile.objects.get)(github_username=owner)
        except:
            return HttpResponseNotFound()

    invalidate = request.GET.get('invalidate', False)
    invalidate = False
    redis = RedisClient.get()
    last_updated = redis.get(f"workflows_updated/{owner}")
    num_cached = len(list(redis.scan_iter(match=f"workflows/{owner}/*")))

    # if user's workflow cache is empty or invalidation is requested, (re)populate it before returning
    if last_updated is None or num_cached == 0:  # or invalidate:
        logger.info(f"GitHub user {owner}'s workflow cache is empty, populating it now")
        refresh_personal_workflows.s(owner).apply_async()

    workflows = [json.loads(redis.get(key)) for key in redis.scan_iter(match=f"workflows/{owner}/*")]
    return JsonResponse({'workflows': workflows})


@sync_to_async
@login_required
@async_to_sync
async def list_org(request, owner):
    pass


@sync_to_async
@login_required
@async_to_sync
async def get(request, owner, name):
    profile = await sync_to_async(Profile.objects.get)(user=request.user)
    invalidate = request.GET.get('invalidate', False)
    workflow = await get_workflow(
        owner=owner,
        name=name,
        github_token=profile.github_token,
        cyverse_token=profile.cyverse_access_token,
        invalidate=bool(invalidate))

    return HttpResponseNotFound() if workflow is None else JsonResponse(workflow)


@sync_to_async
@login_required
@async_to_sync
async def search(request, owner, name):
    profile = await get_user_django_profile(request.user)
    repository = await get_repo(owner, name, profile.github_token)
    return HttpResponseNotFound() if repository is None else JsonResponse(repository)


@sync_to_async
@login_required
@async_to_sync
async def refresh(request, owner, name):
    try:
        workflow = await sync_to_async(Workflow.objects.get)(repo_owner=owner, repo_name=name)
    except:
        return HttpResponseNotFound()

    redis = RedisClient.get()
    profile = await get_user_django_profile(request.user)
    bundle = await workflow_to_dict(workflow, profile.github_token, profile.cyverse_access_token)
    redis.set(f"workflows/{owner}/{name}", json.dumps(del_none(bundle)))
    logger.info(f"Refreshed workflow {owner}/{name}")
    return JsonResponse(bundle)


# @sync_to_async
@login_required
# @async_to_sync
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


@sync_to_async
@login_required
@async_to_sync
async def toggle_public(request, owner, name):
    profile = await get_user_django_profile(request.user)
    if owner != profile.github_username:
        return HttpResponseForbidden()

    try:
        workflow = await sync_to_async(Workflow.objects.get)(user=request.user, repo_owner=owner, repo_name=name)
    except:
        return HttpResponseNotFound()

    redis = RedisClient.get()
    workflow.public = not workflow.public
    await sync_to_async(workflow.save)()
    bundle = await workflow_to_dict(workflow, profile.github_token, profile.cyverse_access_token)
    redis.set(f"workflows/{owner}/{name}/{bundle['branch']['name']}", json.dumps(del_none(bundle)))
    logger.info(f"Workflow {owner}/{name} (branch {bundle['branch']['name']}) is now {'public' if workflow.public else 'private'}")
    return JsonResponse({'workflows': [json.loads(redis.get(key)) for key in redis.scan_iter(match=f"workflows/{owner}/*")]})


@login_required
def bind(request, owner, name):
    # if owner != request.user.profile.github_username:
    #     return HttpResponseForbidden()

    redis = RedisClient.get()
    body = json.loads(request.body.decode('utf-8'))
    body['bound'] = True
    redis.set(f"workflows/{owner}/{name}/{body['branch']['name']}", json.dumps(del_none(body)))
    Workflow.objects.create(user=request.user, repo_owner=owner, repo_name=name, repo_branch=json.dumps(body['branch']), public=False)

    logger.info(f"Created binding for workflow {owner}/{name} as {body['config']['name']} (branch {body['branch']['name']})")
    return JsonResponse({'workflows': [json.loads(redis.get(key)) for key in redis.scan_iter(match=f"workflows/{owner}/*")]})


@login_required
def unbind(request, owner, name):
    # if owner != request.user.profile.github_username:
    #     return HttpResponseForbidden()

    try:
        workflow = Workflow.objects.get(user=request.user, repo_owner=owner, repo_name=name)
    except:
        return HttpResponseNotFound()

    workflow.delete()
    redis = RedisClient.get()
    cached = json.loads(redis.get(f"workflows/{owner}/{name}"))
    cached['public'] = False
    cached['bound'] = False
    redis.set(f"workflows/{owner}/{name}/{cached['branch']['name']}", json.dumps(del_none(cached)))
    logger.info(f"Removed binding for workflow {owner}/{name}")
    return JsonResponse({'workflows': [json.loads(redis.get(key)) for key in redis.scan_iter(match=f"workflows/{owner}/*")]})
