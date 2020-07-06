import json

import requests
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from apis.util import get_config


@login_required
def list(request):
    token = request.user.profile.github_auth_token
    items = requests.get(
        f"https://api.github.com/search/code?q=filename:plantit.yaml+org:computational-plant-science",
        headers={"Authorization": f"token {token}"}
    ).json()['items']
    return JsonResponse({
        'pipelines': [{
            'repo': item['repository'],
            'config': get_config(item['repository'], token)
        } for item in items]
    })


@login_required
def get(request, owner, name):
    token = request.user.profile.github_auth_token
    repo = requests.get(f"https://api.github.com/repos/{owner}/{name}",
                        headers={"Authorization": f"token {token}"}).json()
    config = get_config(repo, token)
    return JsonResponse({
        'repo': repo,
        'config': config
    })


@login_required
def start(request, pipeline, pk):
    params = json.loads(request.body.decode('utf-8'))
    return JsonResponse()
