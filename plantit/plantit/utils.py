from pprint import pprint
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


def cyverse_path_exists(path, token):
    response = requests.get(f"https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path={path}", headers={"Authorization": f"Bearer {token}"})
    content = response.json()
    input_type = 'directory'
    if response.status_code != 200:
        if 'error_code' not in content or ('error_code' in content and content['error_code'] == 'ERR_DOES_NOT_EXIST'):
            path_split = path.rpartition('/')
            base = path_split[0]
            file = path_split[2]
            up_response = requests.get(f"https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path={base}",
                         headers={"Authorization": f"Bearer {token}"})
            up_content = up_response.json()
            if up_response.status_code != 200:
                if 'error_code' not in up_content:
                    print(f"Unknown error: {up_content}")
                    return False
                elif 'error_code' in up_content:
                    print(f"Error: {up_content['error_code']}")
                    return False
            elif 'files' not in up_content:
                print(f"Directory '{base}' does not exist")
                return False
            elif len(up_content['files']) != 1:
                print(f"Multiple files found in directory '{base}' matching name '{file}'")
                return False
            elif up_content['files'][0]['label'] != file:
                print(f"File '{file}' does not exist in directory '{base}'")
                return False
            else:
                input_type = 'file'
        else:
            return False
    return True, input_type


def validate_config(config, token):
    errors = []

    # name (required)
    if 'name' not in config:
        errors.append('Missing attribute \'name\'')
    elif type(config['name']) is not str:
        errors.append('Attribute \'name\' must be a str')

    # author (required)
    if 'author' not in config:
        errors.append('Missing attribute \'author\'')
    elif type(config['author']) is not str:
        errors.append('Attribute \'author\' must be a str')

    # public (required)
    if 'public' not in config:
        errors.append('Missing attribute \'public\'')
    elif type(config['public']) is not bool:
        errors.append('Attribute \'public\' must be a bool')

    # clone (required)
    if 'clone' not in config:
        errors.append('Missing attribute \'clone\'')
    elif type(config['clone']) is not bool:
        errors.append('Attribute \'clone\' must be a bool')

    # image (required)
    if 'image' not in config:
        errors.append('Missing attribute \'image\'')
    elif type(config['image']) is not str:
        errors.append('Attribute \'image\' must be a str')
    else:
        container_split = config['image'].split('/')
        container_name = container_split[-1]
        container_owner = None if container_split[-2] == '' else container_split[-2]
        if 'docker' in config['image'] and not docker_container_exists(container_name, container_owner):
            errors.append(f"Image '{config['image']}' not found on Docker Hub")

    # commands (required)
    if 'commands' not in config:
        errors.append('Missing attribute \'commands\'')
    elif type(config['commands']) is not str:
        errors.append('Attribute \'commands\' must be a str')

    # mount
    if 'mount' in config:
        if type(config['mount']) is not list:
            errors.append('Attribute \'mount\' must be a list')
        elif config['mount'] is None or len(config['mount']) == 0:
            errors.append('Attribute \'mount\' must not be empty')

    # legacy input format
    if 'from' in config:
        errors.append('Attribute \'from\' is obsolete; use an \'input\' section instead')

    # input
    if 'input' in config:
        # path
        if 'path' not in config['input']:
            errors.append('Missing attribute \'input.path\'')
        if config['input']['path'] != '' and config['input']['path'] is not None:
            cyverse_path_result = cyverse_path_exists(config['input']['path'], token)
            if type(cyverse_path_result) is bool and not cyverse_path_result:
                errors.append('Attribute \'input.path\' must be a str (either empty or a valid path in the CyVerse Data Store)')

        # kind
        if 'kind' not in config['input']:
            errors.append('Missing attribute \'input.kind\'')
        if not (config['input']['kind'] == 'file' or config['input']['kind'] == 'files' or config['input']['kind'] == 'directory'):
            errors.append('Attribute \'input.kind\' must be a string (either \'file\', \'files\', or \'directory\')')

        # patterns
        if 'patterns' in config['input'] and type(config['input']['patterns']) is not list or not all(type(pattern) is str for pattern in config['input']['patterns']):
            errors.append('Attribute \'input.patterns\' must be a list of str')

    # legacy output format
    if 'to' in config:
        errors.append('Attribute \'to\' is obsolete; use an \'output\' section instead')

    # output
    if 'output' in config:
        # path
        if 'path' not in config['output']:
            errors.append('Attribute \'output\' must include attribute \'path\'')
        if config['output']['path'] is not None and type(config['output']['path']) is not str:
            errors.append('Attribute \'output.path\' must be a str')

        # include
        if 'include' in config['output']:
            if 'patterns' in config['output']['include']:
                if type(config['output']['include']['patterns']) is not list or not all(
                        type(pattern) is str for pattern in config['output']['include']['patterns']):
                    errors.append('Attribute \'output.include.patterns\' must be a list of str')
            if 'names' in config['output']['include']:
                if type(config['output']['include']['names']) is not list or not all(
                        type(name) is str for name in config['output']['include']['names']):
                    errors.append('Attribute \'output.include.names\' must be a list of str')

        # exclude
        if 'exclude' in config['output']:
            if 'patterns' in config['output']['exclude']:
                if type(config['output']['exclude']['patterns']) is not list or not all(
                        type(pattern) is str for pattern in config['output']['exclude']['patterns']):
                    errors.append('Attribute \'output.exclude.patterns\' must be a list of str')
            if 'names' in config['output']['exclude']:
                if type(config['output']['exclude']['names']) is not list or not all(
                        type(name) is str for name in config['output']['exclude']['names']):
                    errors.append('Attribute \'output.exclude.names\' must be a list of str')

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
