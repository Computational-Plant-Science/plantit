import requests

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse

from plantit.util import get_config


@login_required
def list(request):
    if 'github_auth_token' not in request.session:
        return HttpResponse('Unauthorized for GitHub API', status=401)

    token = request.session['github_auth_token']

    response = requests.get(
        f"https://api.github.com/search/code?q=filename:plantit.yaml+org:computational-plant-science+user:@me",
        headers={"Authorization": f"token {token}"})
    pipelines = [{
        'repo': item['repository'],
        'config': get_config(item['repository'], token)
    } for item in response.json()['items']]

    return JsonResponse({'pipelines': [pipeline for pipeline in pipelines if pipeline['config']['public']]})


@login_required
def get(request, owner, name):
    if 'github_auth_token' not in request.session:
        return HttpResponse('Unauthorized for GitHub API', status=401)

    token = request.session['github_auth_token']
    repo = requests.get(f"https://api.github.com/repos/{owner}/{name}",
                        headers={"Authorization": f"token {token}"}).json()

    return JsonResponse({
        'repo': repo,
        'config': get_config(repo, token)
    })

