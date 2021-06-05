import asyncio
from typing import List

import httpx
import requests
import yaml

from plantit.docker import parse_image_components, image_exists
from plantit.terrain import path_exists


def get_repo(owner: str, name: str, token: str) -> dict:
    repo = requests.get(
        f"https://api.github.com/repos/{owner}/{name}",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
        }).json()
    if 'message' in repo and repo['message'] == 'Not Found': return None

    config = get_repo_config(repo['owner']['login'], repo['name'], token)
    valid = validate_repo_config(config, token)
    if isinstance(valid, bool):
        return {
            'repo': repo,
            'config': config,
            'validation': {
                'is_valid': True,
                'errors': []
            }
        }
    else:
        return {
            'repo': repo,
            'config': config,
            'validation': {
                'is_valid': valid[0],
                'errors': valid[1]
            }
        }


def get_repo_readme(owner: str, name: str, token: str) -> str:
    print(f"Getting README for {owner}/{name}")
    try:
        url = f"https://api.github.com/repos/{owner}/{name}/contents/README.md"
        request = requests.get(url) if token == '' else requests.get(url, headers={"Authorization": f"token {token}"})
        file = request.json()
        return requests.get(file['download_url']).text
    except:
        try:
            url = f"https://api.github.com/repos/{owner}/{name}/contents/README"
            request = requests.get(url) if token == '' else requests.get(url, headers={"Authorization": f"token {token}"})
            file = request.json()
            return requests.get(file['download_url']).text
        except:
            return None


def get_repo_config(owner: str, name: str, token: str) -> dict:
    print(f"Getting config for {owner}/{name}")
    request = requests.get(
        f"https://api.github.com/repos/{owner}/{name}/contents/plantit.yaml") if token == '' \
        else requests.get(f"https://api.github.com/repos/{owner}/{name}/contents/plantit.yaml",
                          headers={"Authorization": f"token {token}"})
    file = request.json()
    content = requests.get(file['download_url']).text
    config = yaml.load(content)

    # fill optional attributes
    config['public'] = config['public'] if 'public' in config else True

    return config


def validate_repo_config(config: dict, token: str) -> (bool, List[str]):
    errors = []

    # name (required)
    if 'name' not in config:
        errors.append('Missing attribute \'name\'')
    elif type(config['name']) is not str:
        errors.append('Attribute \'name\' must be a str')

    # author (optional)
    if 'author' in config:
        author = config['author']
        if (type(author) is str and author == '') or (type(author) is list and not all(type(d) is str for d in author)):
            errors.append('Attribute \'author\' must be a non-empty str or list of str')

    # image (required)
    if 'image' not in config:
        errors.append('Missing attribute \'image\'')
    elif type(config['image']) is not str:
        errors.append('Attribute \'image\' must be a str')
    else:
        image_owner, image_name, image_tag = parse_image_components(config['image'])
        if 'docker' in config['image'] and not image_exists(image_name, image_owner, image_tag):
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

    # gpu
    if 'gpu' in config:
        if type(config['gpu']) is not bool:
            errors.append('Attribute \'mount\' must be a bool')

    # tags
    if 'tags' in config:
        if type(config['tags']) is not list:
            errors.append('Attribute \'tags\' must be a list')

    # legacy input format
    if 'from' in config:
        errors.append('Attribute \'from\' is deprecated; use an \'input\' section instead')

    # input
    if 'input' in config:
        # path
        if 'path' not in config['input']:
            errors.append('Missing attribute \'input.path\'')
        if config['input']['path'] != '' and config['input']['path'] is not None:
            cyverse_path_result = path_exists(config['input']['path'], token)
            if type(cyverse_path_result) is bool and not cyverse_path_result:
                errors.append('Attribute \'input.path\' must be a str (either empty or a valid path in the CyVerse Data Store)')

        # kind
        if 'kind' not in config['input']:
            errors.append('Missing attribute \'input.kind\'')
        if not (config['input']['kind'] == 'file' or config['input']['kind'] == 'files' or config['input']['kind'] == 'directory'):
            errors.append('Attribute \'input.kind\' must be a string (either \'file\', \'files\', or \'directory\')')

        # legacy filetypes format
        if 'patterns' in config['input']:
            errors.append('Attribute \'input.patterns\' is deprecated; use \'input.filetypes\' instead')

        # filetypes
        if 'filetypes' in config['input']:
            if type(config['input']['filetypes']) is not list or not all(type(pattern) is str for pattern in config['input']['filetypes']):
                errors.append('Attribute \'input.filetypes\' must be a list of str')

    # legacy output format
    if 'to' in config:
        errors.append('Attribute \'to\' is deprecated; use an \'output\' section instead')

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

    # doi (optional)
    if 'doi' in config:
        doi = config['doi']
        if (type(doi) is str and doi == '') or (type(doi) is list and not all(type(d) is str for d in doi)):
            errors.append('Attribute \'doi\' must be a non-empty str or list of str')

    return (True, []) if len(errors) == 0 else (False, errors)


def list_connectable_repos_by_owner(owner: str, token: str) -> List[dict]:
    response = requests.get(
        f"https://api.github.com/search/code?q=filename:plantit.yaml+user:{owner}",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
        })
    response_json = response.json()
    workflows = []
    for item in (response_json['items'] if 'items' in response_json else []):
        repo = item['repository']
        config = get_repo_config(item['repository']['owner']['login'], item['repository']['name'], token)
        # readme = get_repo_readme(item['repository']['owner']['login'], item['repository']['name'], token)
        validation = validate_repo_config(config, token)
        workflows.append({
            'repo': repo,
            'config': config,
            # 'readme': readme,
            'validation': {
                'is_valid': validation[0],
                'errors': validation[1]
            }
        })

    return workflows


async def list_connectable_repos_by_owners(owners: List[str], token: str) -> List[dict]:
    urls = [f"https://api.github.com/search/code?q=filename:plantit.yaml+user:{username}" for username in owners]
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
    }

    def fmt(r, t):
        return [{
            'repo': item['repository'],
            'config': get_repo_config(item['repository']['owner']['login'], item['repository']['name'], t),
            # 'get_readme': get_repo_readme(item['repository']['owner']['login'], item['repository']['name'], t)
        } for item in r['items']] if 'items' in r else []

    async with httpx.AsyncClient(headers=headers) as client:
        futures = [client.get(url) for url in urls]
        responses = await asyncio.gather(*futures)
        return [workflow for workflows in [fmt(response.json(), token) for response in responses] for workflow in workflows]
