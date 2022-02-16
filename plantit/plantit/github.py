import asyncio
import logging
from typing import List

import httpx
import requests
import traceback
import yaml
from requests import RequestException, ReadTimeout, Timeout, HTTPError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from plantit.validation import validate_workflow_configuration

logger = logging.getLogger(__name__)


@retry(
    reraise=True,
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
        logger.debug(f"Retrieved GitHub user profile {owner}")
        return profile


@retry(
    reraise=True,
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
    reraise=True,
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
    reraise=True,
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
        if 'message' in jsn and 'OAuth App access restrictions' in jsn['message']:
            logger.warning(jsn['message'])
            return []
        return jsn


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
async def get_repo_readme(owner: str, name: str, token: str, timeout: int = 15) -> str:
    # TODO: are there any other readme variants that GitHub recognizes?
    url1 = f"https://api.github.com/repos/{owner}/{name}/contents/README"
    url2 = f"https://api.github.com/repos/{owner}/{name}/contents/README.md"
    headers = {"Authorization": f"token {token}"}
    async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
        tasks = [client.get(url).json() for url in [url1, url2]]
        results = await asyncio.gather(*tasks)
        response1 = results[0]
        response2 = results[1]

        if response1.status == 200: jsn = response1.json()
        elif response2.status == 200: jsn = response2.json()
        else:
            logger.warning(f"Failed to retrieve README for {owner}/{name}")
            return None

        text = requests.get(jsn['download_url']).text
        logger.info(f"Retrieved README for {owner}/{name}:\n{text}")
        return text


@retry(
    reraise=True,
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
        response = await client.get(f"https://raw.githubusercontent.com/{owner}/{name}/{branch}/plantit.yaml")
        response.raise_for_status()
        config = response.text
        logger.info(f"Retrieved config for {owner}/{name}:\n{config}")
        return yaml.load(config)


async def get_repo_bundle(owner: str, name: str, branch: str, github_token: str, cyverse_token: str) -> dict:
    tasks = [get_repo(owner, name, github_token), get_repo_config(owner, name, github_token, branch)]
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    repo = responses[0]
    config = responses[1]
    valid, errors = validate_workflow_configuration(config)
    return {
        'repo': repo,
        'config': config,
        'validation': {
            'is_valid': valid,
            'errors': errors
        }
    }


@retry(
    reraise=True,
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

        # TODO refactor to send reqs in parallel
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
                    logger.debug(f"No plantit.yaml in {owner}/{repository['name']}/{branch['name']}")
                    continue
                if response.status_code != 200:
                    logger.warning(f"Failed to retrieve plantit.yaml from {owner}/{repository['name']}/{branch['name']}")
                    continue
                else: logger.debug(f"Found plantit.yaml in {owner}/{repository['name']}/{branch['name']}")


                repository['organization'] = owner

                try:
                    config = yaml.safe_load(response.text)
                    valid, errors = validate_workflow_configuration(config)
                    workflows.append({
                        'repo': repository,
                        'config': config,
                        'branch': branch,
                        'validation': {
                            'is_valid': valid,
                            'errors': errors
                        },
                        'example': owner == 'Computational-Plant-Science' and 'example' in repository['name'].lower()
                    })
                except Exception:
                    workflows.append({
                        'repo': repository,
                        'config': {},
                        'branch': branch,
                        'validation': {
                            'is_valid': False,
                            'errors': [traceback.format_exc()]
                        },
                        'example': False
                    })

        return workflows


@retry(
    reraise=True,
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
                    logger.debug(f"No plantit.yaml in {owner}/{repository['name']}/{branch['name']}")
                    continue
                if response.status_code != 200:
                    logger.warning(f"Failed to retrieve plantit.yaml from {owner}/{repository['name']}/{branch['name']}")
                    continue

                try:
                    config = yaml.safe_load(response.text)
                    valid, errors = validate_workflow_configuration(config)
                    workflows.append({
                        'repo': repository,
                        'config': config,
                        'branch': branch,
                        'validation': {
                            'is_valid': valid,
                            'errors': errors
                        }
                    })
                except Exception:
                    workflows.append({
                        'repo': repository,
                        'config': {},
                        'branch': branch,
                        'validation': {
                            'is_valid': False,
                            'errors': [traceback.format_exc()]
                        }
                    })

        return workflows


@retry(
    reraise=True,
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
        if 'message' in jsn and 'OAuth App access restrictions' in jsn['message']:
            logger.warning(jsn['message'])
            return []
        return jsn
