import requests
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from plantit.utils import get_config, validate_config


@login_required
def list_all(request):
    response = requests.get(
        f"https://api.github.com/search/code?q=filename:plantit.yaml-user:Computational-Plant-Science-user:van-der-knaap-lab-user:burke-lab",
        headers={"Authorization": f"token {request.user.profile.github_token}"})
    pipelines = [{
        'repo': item['repository'],
        'config': get_config(item['repository'], request.user.profile.github_token)
    } for item in response.json()['items']]

    return JsonResponse({'pipelines': [pipeline for pipeline in pipelines if pipeline['config']['public']]})


@login_required
def list(request, username):
    response = requests.get(
        f"https://api.github.com/search/code?q=filename:plantit.yaml+user:{username}",
        headers={"Authorization": f"token {request.user.profile.github_token}"})
    pipelines = [{
        'repo': item['repository'],
        'config': get_config(item['repository'], request.user.profile.github_token)
    } for item in response.json()['items']]

    return JsonResponse({'pipelines': [pipeline for pipeline in pipelines if pipeline['config']['public']]})


@login_required
def get(request, username, name):
    repo = requests.get(f"https://api.github.com/repos/{username}/{name}",
                        headers={"Authorization": f"token {request.user.profile.github_token}"}).json()

    return JsonResponse({
        'repo': repo,
        'config': get_config(repo, request.user.profile.github_token)
    })


@login_required
def validate(request, username, name):
    repo = requests.get(f"https://api.github.com/repos/{username}/{name}",
                        headers={"Authorization": f"token {request.user.profile.github_token}"}).json()
    config = get_config(repo, request.user.profile.github_token)
    result = validate_config(config)
    if type(result) is bool and result:
        return JsonResponse({'result': result})
    else:
        return JsonResponse({'result': result[0], 'errors': result[1]})
