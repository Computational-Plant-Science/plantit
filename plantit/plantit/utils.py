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


def docker_container_exists(name, owner=None):
    content = requests.get(
        f"https://hub.docker.com/v2/repositories/{owner if owner is not None else 'library'}/{name}/").json()
    if 'user' not in content or 'name' not in content:
        return False
    if content['user'] != (owner if owner is not None else 'library') or content['name'] != name:
        return False
    return True


def validate_config(config):
    errors = []

    # name
    if 'name' not in config:
        errors.append('Missing attribute \'name\'')
    elif type(config['name']) is not str:
        errors.append('Attribute \'name\' must be a str')
    # author
    if 'author' not in config:
        errors.append('Missing attribute \'author\'')
    elif type(config['author']) is not str:
        errors.append('Attribute \'author\' must be a str')
    # public
    if 'public' not in config:
        errors.append('Missing attribute \'public\'')
    elif type(config['public']) is not bool:
        errors.append('Attribute \'public\' must be a bool')
    # clone
    if 'clone' not in config:
        errors.append('Missing attribute \'clone\'')
    elif type(config['clone']) is not bool:
        errors.append('Attribute \'clone\' must be a bool')
    # image
    if 'image' not in config:
        errors.append('Missing attribute \'image\'')
    elif type(config['image']) is not str:
        errors.append('Attribute \'image\' must be a string')
    else:
        container_split = config['image'].split('/')
        container_name = container_split[-1]
        container_owner = None if container_split[-2] == '' else container_split[-2]
        if not docker_container_exists(container_name, container_owner):
            errors.append(f"Image '{config['image']}' not found on Docker Hub or Sylabs Cloud")
    # commands
    if 'commands' not in config:
        errors.append('Missing attribute \'commands\'')
    elif type(config['commands']) is not str:
        errors.append('Attribute \'commands\' must be a string')

    return True if len(errors) == 0 else (False, errors)


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
