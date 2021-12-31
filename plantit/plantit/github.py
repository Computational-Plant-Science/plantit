import asyncio
import logging
from typing import List

import httpx
import requests
import traceback
import yaml
from requests import RequestException, ReadTimeout, Timeout, HTTPError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from plantit.docker import parse_image_components, image_exists
from plantit.terrain import path_exists

logger = logging.getLogger(__name__)


def validate_repo_config(config: dict, cyverse_token: str) -> (bool, List[str]):
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

    # environment variables
    if 'env' in config:
        if type(config['env']) is not list:
            errors.append('Attribute \'env\' must be a list')
        elif config['env'] is None or len(config['env']) == 0:
            errors.append('Attribute \'env\' must not be empty')

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
            cyverse_path_result = path_exists(config['input']['path'], cyverse_token)
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

    # walltime (optional)
    if 'walltime' in config:
        walltime = config['walltime']
        import re
        pattern = re.compile("^([0-9][0-9]:[0-9][0-9]:[0-9][0-9])$")
        if type(walltime) is not str:
            errors.append('Attribute \'walltime\' must be a str')
        if type(walltime) is str and not bool(pattern.match(walltime)):
            errors.append('Attribute \'walltime\' must have format XX:XX:XX')

    return (True, []) if len(errors) == 0 else (False, errors)


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
async def get_profile(owner: str, token: str) -> dict:
    headers = {'Authorization': f"Bearer {token}"}
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.get(f"https://api.github.com/users/{owner}")
        if response.status_code != 200: raise ValueError(f"Bad response from GitHub for user {owner}: {response.status_code}")

        profile = response.json()
        logger.debug(f"Retrieved GitHub user profile {owner}:\n{profile}")
        return profile


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
async def get_repo(owner: str, name: str, token: str) -> dict:
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
    }
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.get(
            f"https://api.github.com/repos/{owner}/{name}",
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
            })
        repo = response.json()
        if 'message' in repo and repo['message'] == 'Not Found': raise ValueError(f"Repo {owner}/{name} not found")
        logger.info(f"Retrieved repo {owner}/{name}:\n{repo}")
        return repo


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
async def list_repo_branches(owner: str, name: str, token: str) -> list:
    headers = {
        "Authorization": f"token {token}",
    }
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.get(f"https://api.github.com/repos/{owner}/{name}/branches")
        branches = response.json()
        return branches


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
async def list_repositories(owner: str, token: str) -> list:
    headers = {
        "Authorization": f"token {token}",
    }
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.get(f"https://api.github.com/users/{owner}/repos")
        jsn = response.json()
        # if 'message' in jsn and 'OAuth App access restrictions' in jsn['message']: raise ValueError(jsn['message'])
        if 'message' in jsn and 'OAuth App access restrictions' in jsn['message']:
            logger.warning(jsn['message'])
            return []
        return jsn


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
def get_repo_readme(owner: str, name: str, token: str) -> str:
    # TODO refactor to use asyncx
    try:
        url = f"https://api.github.com/repos/{owner}/{name}/contents/README.md"
        request = requests.get(url) if token == '' else requests.get(url, headers={"Authorization": f"token {token}"})
        file = request.json()
        text = requests.get(file['download_url']).text
        logger.info(f"Retrieved README for {owner}/{name}:\n{text}")
        return text
    except:
        try:
            url = f"https://api.github.com/repos/{owner}/{name}/contents/README"
            request = requests.get(url) if token == '' else requests.get(url, headers={"Authorization": f"token {token}"})
            file = request.json()
            text = requests.get(file['download_url']).text
            logger.info(f"Retrieved README for {owner}/{name}:\n{text}")
            return text
        except:
            logger.warning(f"Failed to retrieve README for {owner}/{name}")
            return None


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
async def get_repo_config(owner: str, name: str, token: str, branch: str = 'master') -> dict:
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
    }
    async with httpx.AsyncClient(headers=headers) as client:
        # response = await client.get(
        #     f"https://api.github.com/repos/{owner}/{name}/contents/plantit.yaml") if token == '' \
        #     else requests.get(f"https://api.github.com/repos/{owner}/{name}/contents/plantit.yaml",
        #                       headers={"Authorization": f"token {token}"})
        response = await client.get(f"https://raw.githubusercontent.com/{owner}/{name}/{branch}/plantit.yaml")
        config = response.text
        logger.info(f"Retrieved config for {owner}/{name}:\n{config}")
        # config = await client.get(response.json()['download_url']).text
        return yaml.load(config)


async def get_repo_bundle(owner: str, name: str, branch: str, github_token: str, cyverse_token: str) -> dict:
    tasks = [get_repo(owner, name, github_token), get_repo_config(owner, name, github_token, branch)]
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    repo = responses[0]
    config = responses[1]
    valid = validate_repo_config(config, cyverse_token)
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


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
async def list_connectable_repos_by_org(owner: str, token: str) -> List[dict]:
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
    }
    async with httpx.AsyncClient(headers=headers) as client:
        workflows = []
        org_repos = await list_repositories(owner, token)

        for repository in org_repos:
            branches = await list_repo_branches(owner, repository['name'], token)
            for branch in branches:
                response = await client.get(
                    f"https://raw.githubusercontent.com/{owner}/{repository['name']}/{branch['name']}/plantit.yaml",
                    headers={
                        "Authorization": f"token {token}",
                        "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
                    })

                if response.status_code == 404:
                    logger.info(f"No plantit.yaml in {owner}/{repository['name']}/{branch['name']}")
                    continue
                if response.status_code != 200:
                    logger.warning(f"Failed to retrieve plantit.yaml from {owner}/{repository['name']}/{branch['name']}")
                    continue

                repository['organization'] = owner

                try:
                    config = yaml.safe_load(response.text)
                    validation = validate_repo_config(config, token)
                    workflows.append({
                        'repo': repository,
                        'config': config,
                        'branch': branch,
                        # 'readme': readme,
                        'validation': {
                            'is_valid': validation[0],
                            'errors': validation[1]
                        }
                    })
                except Exception:
                    workflows.append({
                        'repo': repository,
                        'config': {},
                        'branch': branch,
                        # 'readme': readme,
                        'validation': {
                            'is_valid': False,
                            'errors': [traceback.format_exc()]
                        }
                    })

        return workflows


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
async def list_connectable_repos_by_owner(owner: str, token: str) -> List[dict]:
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
    }
    async with httpx.AsyncClient(headers=headers) as client:
        workflows = []
        owned_repos = await list_repositories(owner, token)
        for repository in owned_repos:
            branches = await list_repo_branches(owner, repository['name'], token)
            for branch in branches:
                response = await client.get(
                    f"https://raw.githubusercontent.com/{owner}/{repository['name']}/{branch['name']}/plantit.yaml",
                    headers={
                        "Authorization": f"token {token}",
                        "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
                    })

                if response.status_code == 404:
                    logger.info(f"No plantit.yaml in {owner}/{repository['name']}/{branch['name']}")
                    continue
                if response.status_code != 200:
                    logger.warning(f"Failed to retrieve plantit.yaml from {owner}/{repository['name']}/{branch['name']}")
                    continue

                try:
                    config = yaml.safe_load(response.text)
                    validation = validate_repo_config(config, token)
                    workflows.append({
                        'repo': repository,
                        'config': config,
                        'branch': branch,
                        # 'readme': readme,
                        'validation': {
                            'is_valid': validation[0],
                            'errors': validation[1]
                        }
                    })
                except Exception:
                    workflows.append({
                        'repo': repository,
                        'config': {},
                        'branch': branch,
                        # 'readme': readme,
                        'validation': {
                            'is_valid': False,
                            'errors': [traceback.format_exc()]
                        }
                    })

        return workflows


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
async def list_user_organizations(username: str, token: str) -> List[dict]:
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
    }
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.get(f"https://api.github.com/users/{username}/orgs")
        if response.status_code != 200: logger.error(f"Failed to retrieve organizations for {username}")
        jsn = response.json()
        # if 'message' in jsn and 'OAuth App access restrictions' in jsn['message']: raise ValueError(jsn['message'])
        if 'message' in jsn and 'OAuth App access restrictions' in jsn['message']:
            logger.warning(jsn['message'])
            return []
        return jsn
        # return response.json()
