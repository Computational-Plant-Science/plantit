import asyncio
import json

import httpx
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse

from plantit import settings
from plantit.redis import RedisClient
from plantit.runs.utils import list_workflows_for_users
from plantit.utils import get_repo_config, validate_workflow_config, get_repo_readme
from plantit.workflows.utils import refresh_workflow


@login_required
def list_all(request):
    redis = RedisClient.get()
    users = User.objects.exclude(profile__isnull=True).all()

    with open(settings.MORE_USERS, 'r') as file:
        more_users = json.load(file)
        usernames = [user.profile.github_username for user in users] + more_users
        workflows = [json.loads(redis.get(key)) for key in redis.scan_iter(match='workflow/*')]

        if len(workflows) == 0:
            print(f"Populating workflow cache")
            workflows = asyncio.run(list_workflows_for_users(usernames, request.user.profile.github_token))
            for workflow in workflows:
                redis.set(f"workflow/{workflow['repo']['owner']['login']}/{workflow['repo']['name']}", json.dumps(workflow))

    return JsonResponse({'workflows': workflows})


@login_required
def refresh_all(request):
    redis = RedisClient.get()
    users = User.objects.all()

    with open(settings.MORE_USERS, 'r') as file:
        more_users = json.load(file)
        usernames = [user.profile.github_username for user in users] + more_users

        print(f"Refreshing workflow cache")
        workflows = asyncio.run(list_workflows_for_users(usernames, request.user.profile.github_token))
        for workflow in workflows:
            redis.set(f"workflow/{workflow['repo']['owner']['login']}/{workflow['repo']['name']}", json.dumps(workflow))

    return JsonResponse({'workflows': workflows})


@login_required
def list_by_user(request, username):
    workflows = asyncio.run(list_workflows_for_users([username], request.user.profile.github_token))
    return JsonResponse({'workflows': workflows})


@login_required
def get(request, username, name):
    redis = RedisClient.get()
    workflow = redis.get(f"workflow/{username}/{name}")
    if workflow is not None:
        return JsonResponse(json.loads(workflow))
    else:
        workflow = refresh_workflow(username, name, request.user.profile.github_token)
        result = validate_workflow_config(workflow['config'], request.user.profile.cyverse_token)
        if not isinstance(result, bool):
            workflow['validation_errors'] = result[1]

        redis.set(f"workflow/{username}/{name}", json.dumps(workflow))
        return JsonResponse(workflow)


@login_required
def get_readme(request, username, name):
    readme = get_repo_readme(name, username, request.user.profile.github_token)
    return JsonResponse({'readme': readme})


@login_required
def refresh(request, username, name):
    redis = RedisClient.get()
    workflow = refresh_workflow(username, name, request.user.profile.github_token)
    redis.set(f"workflow/{username}/{name}", json.dumps(workflow))
    return JsonResponse(workflow)


@login_required
def validate(request, username, name):
    headers = {"Authorization": f"token {request.user.profile.github_token}"}
    with httpx.Client(headers=headers) as client:
        response = client.get(f"https://api.github.com/repos/{username}/{name}")
        repo = response.json()
        config = get_repo_config(repo['name'], repo['owner']['login'], request.user.profile.github_token)
        result = validate_workflow_config(config, request.user.profile.cyverse_token)
        if isinstance(result, bool):
            return JsonResponse({'result': result})
        else:
            return JsonResponse({'result': result[0], 'errors': result[1]})
