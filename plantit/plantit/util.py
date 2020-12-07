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


def singularity_image_exists(image):
    content = requests.get(f"https://library.sylabs.io/v1/search?model=Container&value={image}").json()
    if 'container' not in content['data']:
        return False
    if 'container' in content['data']:
        if len(content['data']['container']) != 1:
            return False
    return True


def docker_image_exists(image):
    content = requests.get(f"https://hub.docker.com/api/content/v1/products/search?q={image}&page=1&page_size=4")
    if 'count' not in content['data']:
        return False
    if content['data']['count'] != 1:
        return False
    return True


def validate_config(config):
    errors = []

    # name
    if 'name' not in config:
        errors.append('Missing attribute \'name\'')
    elif type(config['name']) is not str:
        errors.append('Attribute \'name\' must be a bool')
    # author
    if 'author' not in config:
        errors.append('Missing attribute \'author\'')
    elif type(config['author']) is not bool:
        errors.append('Attribute \'author\' must be a bool')
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
    elif not singularity_image_exists(config['image']) and not docker_image_exists(config['image']):
        errors.append(f"Image '{config['image']}' not found on Docker Hub or Sylabs Cloud")
    # commands
    if 'commands' not in config:
        errors.append('Missing attribute \'commands\'')
    elif type(config['commands']) is not str:
        errors.append('Attribute \'commands\' must be a string')

    return True if len(errors) == 0 else False, errors


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
