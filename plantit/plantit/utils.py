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
        # elif content['error_code'] == 'ERR_UNCHECKED_EXCEPTION':
        #     return False
        else:
            return False
    return True, input_type


def validate_config(config, token):
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
        errors.append('Attribute \'image\' must be a str')
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
        errors.append('Attribute \'commands\' must be a str')
    # input
    input_type = 'none'
    if 'from' in config:
        if config['from'] != '':
            cyverse_path_result = cyverse_path_exists(config['from'], token)
            if type(cyverse_path_result) is bool and not cyverse_path_result:
                errors.append('Attribute \'from\' must be a string (either empty or a valid path in the CyVerse Data Store)')
            else:
                input_type = cyverse_path_result[1] if cyverse_path_result[1] == 'file' else ('directory' if 'from_directory' in config and config['from_directory'] else 'files')
        if 'from_directory' in config and type(config['from_directory']) is not bool:
            errors.append('Attribute \'from_directory\' must be a bool')
    elif 'from_directory' in config:
        errors.append('Attribute \'from_directory\' may only be configured in combination with attribute \'from\'')
    # output
    if 'to' in config and type(config['to']) is not str:
        errors.append('Attribute \'to\' must be a str')

    return (True, input_type) if len(errors) == 0 else (False, errors)


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
