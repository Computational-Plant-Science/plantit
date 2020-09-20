import requests

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse

from plantit.util import get_config


@login_required
def list(request):
    response = requests.get(
        f"https://api.github.com/search/code?q=filename:plantit.yaml+org:computational-plant-science+user:@me",
        headers={"Authorization": f"token {request.user.profile.github_token}"})
    pipelines = [{
        'repo': item['repository'],
        'config': get_config(item['repository'], request.user.profile.github_token)
    } for item in response.json()['items']]

    return JsonResponse({'pipelines': [pipeline for pipeline in pipelines if pipeline['config']['public']]})


@login_required
def get(request, owner, name):
    repo = requests.get(f"https://api.github.com/repos/{owner}/{name}",
                        headers={"Authorization": f"token {request.user.profile.github_token}"}).json()

    return JsonResponse({
        'repository': repo,
        'config': get_config(repo, request.user.profile.github_token)
    })

