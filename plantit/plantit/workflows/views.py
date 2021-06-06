import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseForbidden
from rest_framework.decorators import api_view

from plantit.github import get_repo_readme, get_repo
from plantit.redis import RedisClient
from plantit.users.models import Profile
from plantit.workflows.models import Workflow
from plantit.workflows.utils import bind_workflow, get_personal_workflows, get_public_workflows, get_workflow

logger = logging.getLogger(__name__)


@api_view(['GET'])
@login_required
def list_public(request):
    invalidate = request.GET.get('invalidate', False)
    workflows = get_public_workflows(token=request.user.profile.github_token, invalidate=bool(invalidate))
    return JsonResponse({'workflows': workflows})


@api_view(['GET'])
@login_required
def list_personal(request, owner):
    if owner != request.user.profile.github_username:
        try:
            Profile.objects.get(github_username=owner)
        except:
            return HttpResponseNotFound()

    invalidate = request.GET.get('invalidate', False)
    workflows = get_personal_workflows(owner=owner, invalidate=bool(invalidate))
    return JsonResponse({'workflows': workflows})


@api_view(['GET'])
@login_required
def get(request, owner, name):
    invalidate = request.GET.get('invalidate', False)
    workflow = get_workflow(owner=owner, name=name, token=request.user.profile.github_token, invalidate=bool(invalidate))
    return HttpResponseNotFound() if workflow is None else JsonResponse(workflow)


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
    workflow = bind_workflow(workflow, request.user.profile.github_token)
    redis.set(f"workflows/{owner}/{name}", json.dumps(workflow))
    logger.info(f"Refreshed workflow {owner}/{name}")
    return JsonResponse(workflow)


@api_view(['GET'])
@login_required
def readme(request, owner, name):
    return JsonResponse({'readme': get_repo_readme(name, owner, request.user.profile.github_token)})


@api_view(['POST'])
@login_required
def connect(request, owner, name):
    if owner != request.user.profile.github_username:
        return HttpResponseForbidden()

    redis = RedisClient.get()
    request.data['connected'] = True
    redis.set(f"workflows/{owner}/{name}", json.dumps(request.data))
    Workflow.objects.create(user=request.user, repo_owner=owner, repo_name=name, public=False)
    logger.info(f"Connected workflow {owner}/{name} as {request.data['config']['name']}")
    return JsonResponse({'workflows': [json.loads(redis.get(key)) for key in redis.scan_iter(match=f"workflows/{owner}/*")]})


@api_view(['POST'])
@login_required
def toggle_public(request, owner, name):
    if owner != request.user.profile.github_username:
        return HttpResponseForbidden()

    try:
        workflow = Workflow.objects.get(user=request.user, repo_owner=owner, repo_name=name)
    except:
        return HttpResponseNotFound()

    redis = RedisClient.get()
    workflow.public = not workflow.public
    workflow.save()
    redis.set(f"workflows/{owner}/{name}", json.dumps(bind_workflow(workflow, request.user.profile.github_token)))
    logger.info(f"Workflow {owner}/{name} is now {'public' if workflow.public else 'private'}")
    return JsonResponse({'workflows': [json.loads(redis.get(key)) for key in redis.scan_iter(match=f"workflows/{owner}/*")]})


@api_view(['DELETE'])
@login_required
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
