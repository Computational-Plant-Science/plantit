from random import choice

import requests
import yaml


def get_config(repo, token):
    request = requests.get(
        f"https://api.github.com/repos/{repo['owner']['login']}/{repo['name']}/contents/plantit.yaml") if token == '' \
        else requests.get(f"https://api.github.com/repos/{repo['owner']['login']}/{repo['name']}/contents/plantit.yaml",
                          headers={"Authorization": f"token {token}"})
    file = request.json()
    content = requests.get(file['download_url']).text
    return yaml.load(content)


def csrf_token(request):
    token = request.session.get('csrfToken', None)
    if token is None:
        token = secret_key()
        request.session['csrfToken'] = token
    return token


def random_string(length, allowed_chars='abcdefghijklmnopqrstuvwxyz' 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    return ''.join(choice(allowed_chars) for i in range(length))


def secret_key():
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return random_string(40, chars)
