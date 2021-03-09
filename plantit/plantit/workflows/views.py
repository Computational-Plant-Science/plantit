import asyncio
import json
from datetime import datetime
from pathlib import Path

import httpx
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse

from plantit import settings
from plantit.runs.utils import list_workflows_for_users
from plantit.utils import get_repo_config, validate_workflow_config


@login_required
def list_all(request):
    workflows_file = settings.WORKFLOWS_CACHE
    workflows_path = Path(workflows_file)
    refresh_minutes = int(settings.WORKFLOWS_REFRESH_MINUTES)

    users = User.objects.all()
    usernames = [user.profile.github_username for user in users] + ['Computational-Plant-Science', 'van-der-knaap-lab', 'burke-lab']

    if not workflows_path.exists():
        print(f"Creating workflow cache")
        workflows = asyncio.run(list_workflows_for_users(usernames, request.user.profile.github_token))
        with open(workflows_file, 'w') as file:
            json.dump(workflows, file)
    else:
        now = datetime.now()
        last_modified = datetime.fromtimestamp(workflows_path.stat().st_ctime)
        elapsed_minutes = (now - last_modified).total_seconds() / 60.0

        if elapsed_minutes < refresh_minutes:
            with open(workflows_file, 'r') as file:
                workflows = json.load(file)
        else:
            print(f"Workflow cache is stale, refreshing")
            workflows = asyncio.run(list_workflows_for_users(usernames, request.user.profile.github_token))
            with open(workflows_file, 'w') as file:
                json.dump(workflows, file)

    return JsonResponse({'workflows': workflows})


@login_required
def list_by_user(request, username):
    workflows = asyncio.run(list_workflows_for_users([username], request.user.profile.github_token))
    return JsonResponse({'workflows': workflows})


@login_required
def get(request, username, name):
    headers = {
        "Authorization": f"token {request.user.profile.github_token}",
        "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
    }

    with httpx.Client(headers=headers) as client:
        response = client.get(f"https://api.github.com/repos/{username}/{name}")
        repo = response.json()
        return JsonResponse({
            'repo': repo,
            'config': get_repo_config(repo['name'], repo['owner']['login'], request.user.profile.github_token)
        })


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
