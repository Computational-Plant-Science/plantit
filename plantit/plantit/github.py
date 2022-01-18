import asyncio
import logging
from typing import List

import httpx
import requests
import traceback
import yaml
from requests import RequestException, ReadTimeout, Timeout, HTTPError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from plantit.task_configuration import validate_task_configuration

logger = logging.getLogger(__name__)


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
async def get_profile(owner: str, token: str, timeout: int = 15) -> dict:
    headers = {'Authorization': f"Bearer {token}"}
    async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
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
async def get_repo(owner: str, name: str, token: str, timeout: int = 15) -> dict:
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
    }
    async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
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
async def list_repo_branches(owner: str, name: str, token: str, timeout: int = 15) -> list:
    headers = {
        "Authorization": f"token {token}",
    }
    async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
        response = await client.get(f"https://api.github.com/repos/{owner}/{name}/branches")
        branches = response.json()
        return branches


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
async def list_repositories(owner: str, token: str, timeout: int = 15) -> list:
    headers = {
        "Authorization": f"token {token}",
    }
    async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
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
def get_repo_readme(owner: str, name: str, token: str, timeout: int = 15) -> str:
    # TODO refactor to use asyncx
    try:
        url = f"https://api.github.com/repos/{owner}/{name}/contents/README.md"
        request = requests.get(url, timeout=timeout) if token == '' else requests.get(url, headers={"Authorization": f"token {token}"})
        file = request.json()
        text = requests.get(file['download_url']).text
        logger.info(f"Retrieved README for {owner}/{name}:\n{text}")
        return text
    except:
        try:
            url = f"https://api.github.com/repos/{owner}/{name}/contents/README"
            request = requests.get(url, timeout=timeout) if token == '' else requests.get(url, headers={"Authorization": f"token {token}"})
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
async def get_repo_config(owner: str, name: str, token: str, branch: str = 'master', timeout: int = 15) -> dict:
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
    }
    async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
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
    valid = validate_task_configuration(config, cyverse_token)
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
async def list_connectable_repos_by_org(owner: str, token: str, timeout: int = 15) -> List[dict]:
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
    }
    async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
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
                    validation = validate_task_configuration(config, token)
                    workflows.append({
                        'repo': repository,
                        'config': config,
                        'branch': branch,
                        # 'readme': readme,
                        'validation': {
                            'is_valid': validation[0],
                            'errors': validation[1]
                        },
                        'example': owner == 'Computational-Plant-Science' and 'example' in repository['name'].lower()
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
async def list_connectable_repos_by_owner(owner: str, token: str, timeout: int = 15) -> List[dict]:
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
    }
    async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
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
                    validation = validate_task_configuration(config, token)
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
async def list_user_organizations(username: str, token: str, timeout: int = 15) -> List[dict]:
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
    }
    async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
        response = await client.get(f"https://api.github.com/users/{username}/orgs")
        if response.status_code != 200: logger.error(f"Failed to retrieve organizations for {username}")
        jsn = response.json()
        # if 'message' in jsn and 'OAuth App access restrictions' in jsn['message']: raise ValueError(jsn['message'])
        if 'message' in jsn and 'OAuth App access restrictions' in jsn['message']:
            logger.warning(jsn['message'])
            return []
        return jsn
        # return response.json()
