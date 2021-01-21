import asyncio
import json
from datetime import datetime
from os.path import join
from pathlib import Path

import requests
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User

from plantit import settings
from plantit.runs.utils import __list_by_user, __list_all_by_user
from plantit.utils import get_repo_config, validate_config


@login_required
def list_all(request):
    flows_file = settings.FLOWS_CACHE
    flows_path = Path(flows_file)
    flows_refresh = int(settings.FLOWS_REFRESH_MINUTES)
    flows_file = settings.FLOWS_CACHE
    flows = []
    users = User.objects.all()
    usernames = [user.profile.github_username for user in users] + ['Computational-Plant-Science',
                                                                    'van-der-knaap-lab', 'burke-lab']

    if not flows_path.exists():
        print(f"No flows cached, retrieving")
        for username in usernames:
            flows = flows + __list_by_user(username, request.user.profile.github_token)
        with open(flows_file, 'w') as file:
            json.dump(flows, file)
    else:
        now = datetime.now()
        modified = datetime.fromtimestamp(flows_path.stat().st_ctime)
        if ((now - modified).total_seconds() / 60.0) < flows_refresh:
            print(f"Using flows cached in: {flows_file}")
            with open(flows_file, 'r') as file:
                flows = json.load(file)
        else:
            print(f"Flow cache is stale, refreshing")
            flows = asyncio.run(__list_all_by_user(usernames, request.user.profile.github_token))
            with open(flows_file, 'w') as file:
                json.dump(flows, file)

    return JsonResponse({'flows': flows})


@login_required
def list_by_user(request, username):
    return JsonResponse({'flows': __list_by_user(username, request.user.profile.github_token)})


@login_required
def get(request, username, name):
    repo = requests.get(f"https://api.github.com/repos/{username}/{name}",
                        headers={
                            "Authorization": f"token {request.user.profile.github_token}",
                            "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
                        }).json()

    return JsonResponse({
        'repo': repo,
        'config': get_repo_config(repo['name'], repo['owner']['login'], request.user.profile.github_token)
    })


@login_required
def validate(request, username, name):
    repo = requests.get(f"https://api.github.com/repos/{username}/{name}",
                        headers={"Authorization": f"token {request.user.profile.github_token}"}).json()
    config = get_repo_config(repo['name'], repo['owner']['login'], request.user.profile.github_token)
    result = validate_config(config, request.user.profile.cyverse_token)
    if isinstance(result, bool):
        return JsonResponse({'result': result})
    else:
        return JsonResponse({'result': result[0], 'errors': result[1]})
