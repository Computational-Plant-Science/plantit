import asyncio
import logging
from typing import List, Optional

import httpx
import requests
import traceback
import yaml
from requests import RequestException, ReadTimeout, Timeout, HTTPError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from plantit.validation import validate_workflow_configuration

logger = logging.getLogger(__name__)


class GitHubClient:
    def __init__(self, access_token: str, timeout_seconds: int = 15):
        self.__logger = logging.getLogger(__name__)
        self.__token = access_token
        self.__timeout = timeout_seconds

    @retry(
        reraise=True,
        wait=wait_exponential(multiplier=1, min=4, max=10),
        stop=stop_after_attempt(3),
        retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
            RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
            Timeout) | retry_if_exception_type(HTTPError)))
    def get_profile(self,
                    owner: str,
                    token: Optional[str] = None, timeout: Optional[int] = None) -> dict:
        headers = {'Authorization': f"Bearer {token if token is not None else self.__token}"}
        response = requests.get(f"https://api.github.com/users/{owner}",
                                headers=headers,
                                timeout=timeout if timeout is not None else self.__timeout)
        response.raise_for_status()

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
    async def get_repo(self,
                       owner: str,
                       name: str,
                       token: Optional[str] = None,
                       timeout: Optional[int] = None) -> dict:
        response = requests.get(
            f"https://api.github.com/repos/{owner}/{name}",
            headers={
                "Authorization": f"token {token if token is not None else self.__token}",
                "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
            },
            timeout=timeout if timeout is not None else self.__timeout)
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
    def list_repo_branches(self,
                                 owner: str,
                                 name: str,
                                 token: Optional[str] = None,
                                 timeout: Optional[int] = None) -> list:
        headers = {
            "Authorization": f"token {token if token is not None else self.__token}",
        }
        response = requests.get(f"https://api.github.com/repos/{owner}/{name}/branches",
                                headers=headers,
                                timeout=timeout if timeout is not None else self.__timeout)
        branches = response.json()
        return branches

    @retry(
        reraise=True,
        wait=wait_exponential(multiplier=1, min=4, max=10),
        stop=stop_after_attempt(3),
        retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
            RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
            Timeout) | retry_if_exception_type(HTTPError)))
    def list_repositories(self,
                          owner: str,
                          token: Optional[str] = None,
                          timeout: Optional[int] = None) -> list:
        headers = {
            "Authorization": f"token {token if token is not None else self.__token}",
        }
        response = requests.get(f"https://api.github.com/users/{owner}/repos",
                                headers=headers,
                                timeout=timeout if timeout is not None else self.__timeout)
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
    def get_repo_readme(self,
                        owner: str,
                        name: str,
                        token: Optional[str] = None,
                        timeout: Optional[int] = None) -> Optional[str]:
        # TODO: are there any other readme variants that GitHub recognizes?
        url1 = f"https://api.github.com/repos/{owner}/{name}/contents/README"
        url2 = f"https://api.github.com/repos/{owner}/{name}/contents/README.md"
        headers = {"Authorization": f"token {token if token is not None else self.__token}"}
        response1 = requests.get(url1, headers=headers, timeout=timeout if timeout is not None else self.__timeout)
        response2 = requests.get(url2, headers=headers, timeout=timeout if timeout is not None else self.__timeout)

        if response1.status_code == 200:
            jsn = response1.json()
        elif response2.status_code == 200:
            jsn = response2.json()
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
    def get_repo_config(self,
                        owner: str,
                        name: str,
                        branch: str = 'master',
                        token: Optional[str] = None,
                        timeout: Optional[int] = None) -> dict:
        headers = {
            "Authorization": f"token {token if token is not None else self.__token}",
            "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
        }
        response = requests.get(f"https://raw.githubusercontent.com/{owner}/{name}/{branch}/plantit.yaml",
                                headers=headers,
                                timeout=timeout if timeout is not None else self.__timeout)
        response.raise_for_status()
        config = response.text
        logger.info(f"Retrieved config for {owner}/{name}:\n{config}")
        return yaml.load(config)

    def get_repo_bundle(self,
                        owner: str,
                        name: str,
                        branch: str,
                        token: Optional[str] = None,
                        timeout: Optional[int] = None) -> dict:

        repo = self.get_repo(owner, name, token, timeout)
        config = self.get_repo_config(owner, name, branch, token, timeout)
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
    def list_connectable_repos_by_org(self,
                                      owner: str,
                                      token: Optional[str] = None,
                                      timeout: Optional[int] = None) -> List[dict]:
        workflows = []
        org_repos = self.list_repositories(owner, token, timeout)

        # TODO refactor to send reqs in parallel
        for repository in org_repos:
            branches = self.list_repo_branches(owner, repository['name'], token, timeout)
            for branch in branches:
                response = requests.get(
                    f"https://raw.githubusercontent.com/{owner}/{repository['name']}/{branch['name']}/plantit.yaml",
                    headers={
                        "Authorization": f"token {token if token is not None else self.__token}",
                        "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
                    },
                    timeout=timeout if timeout is not None else self.__timeout)

                if response.status_code == 404:
                    logger.debug(f"No plantit.yaml in {owner}/{repository['name']}/{branch['name']}")
                    continue
                if response.status_code != 200:
                    logger.warning(f"Failed to retrieve plantit.yaml from {owner}/{repository['name']}/{branch['name']}")
                    continue
                else:
                    logger.debug(f"Found plantit.yaml in {owner}/{repository['name']}/{branch['name']}")

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
    def list_connectable_repos_by_owner(self,
                                        owner: str,
                                        token: Optional[str] = None,
                                        timeout: Optional[int] = None) -> List[dict]:
        workflows = []
        owned_repos = self.list_repositories(owner, token, timeout)
        for repository in owned_repos:
            branches = self.list_repo_branches(owner, repository['name'], token, timeout)
            for branch in branches:
                response = requests.get(
                    f"https://raw.githubusercontent.com/{owner}/{repository['name']}/{branch['name']}/plantit.yaml",
                    headers={
                        "Authorization": f"token {token if token is not None else self.__token}",
                        "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
                    },
                    timeout=timeout if timeout is not None else self.__timeout)

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
    def list_user_organizations(self,
                                username: str,
                                token: Optional[str] = None,
                                timeout: Optional[int] = None) -> List[dict]:
        headers = {
            "Authorization": f"token {token if token is not None else self.__token}",
            "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
        }
        response = requests.get(f"https://api.github.com/users/{username}/orgs",
                                headers=headers,
                                timeout=timeout if timeout is not None else self.__timeout)
        if response.status_code != 200: logger.error(f"Failed to retrieve organizations for {username}")
        jsn = response.json()
        if 'message' in jsn and 'OAuth App access restrictions' in jsn['message']:
            logger.warning(jsn['message'])
            return []
        return jsn


class AsyncGitHubClient:
    def __init__(self, access_token: str, timeout_seconds: int = 15):
        self.__logger = logging.getLogger(__name__)
        self.__token = access_token
        self.__timeout = timeout_seconds

    @retry(
        reraise=True,
        wait=wait_exponential(multiplier=1, min=4, max=10),
        stop=stop_after_attempt(3),
        retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
            RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
            Timeout) | retry_if_exception_type(HTTPError)))
    async def get_profile_async(self,
                                owner: str,
                                token: Optional[str] = None,
                                timeout: Optional[int] = None) -> dict:
        headers = {'Authorization': f"Bearer {token if token is not None else self.__token}"}
        async with httpx.AsyncClient(headers=headers, timeout=timeout if timeout is not None else self.__timeout) as client:
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
    async def get_repo_async(self,
                             owner: str,
                             name: str,
                             token: Optional[str] = None,
                             timeout: Optional[int] = None) -> dict:
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
    async def list_repo_branches_async(self,
                                       owner: str,
                                       name: str,
                                       token: Optional[str] = None,
                                       timeout: Optional[int] = None) -> list:
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
    async def list_repositories_async(self,
                                      owner: str,
                                      token: Optional[str] = None,
                                      timeout: Optional[int] = None) -> list:
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
    async def get_repo_readme_async(self,
                                    owner: str,
                                    name: str,
                                    token: Optional[str] = None,
                                    timeout: Optional[int] = None) -> str:
        # TODO: are there any other readme variants that GitHub recognizes?
        url1 = f"https://api.github.com/repos/{owner}/{name}/contents/README"
        url2 = f"https://api.github.com/repos/{owner}/{name}/contents/README.md"
        headers = {"Authorization": f"token {token}"}
        async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
            tasks = [client.get(url).json() for url in [url1, url2]]
            results = await asyncio.gather(*tasks)
            response1 = results[0]
            response2 = results[1]

            if response1.status == 200:
                jsn = response1.json()
            elif response2.status == 200:
                jsn = response2.json()
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
    async def get_repo_config_async(self,
                                    owner: str,
                                    name: str,
                                    branch: str = 'master',
                                    token: Optional[str] = None,
                                    timeout: Optional[int] = None) -> dict:
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

    async def get_repo_bundle_async(self,
                                    owner: str,
                                    name: str,
                                    branch: str,
                                    token: Optional[str] = None,
                                    timeout: Optional[int] = None) -> dict:
        tasks = [self.get_repo_async(owner, name, token, timeout), self.get_repo_config_async(owner, name, branch, token, timeout)]
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
    async def list_connectable_repos_by_org_async(self,
                                                  owner: str,
                                                  token: Optional[str] = None,
                                                  timeout: Optional[int] = None) -> List[dict]:
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
        }
        async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
            workflows = []
            org_repos = await self.list_repositories_async(owner, token)

            # TODO refactor to send reqs in parallel
            for repository in org_repos:
                branches = await self.list_repo_branches_async(owner, repository['name'], token)
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
                    else:
                        logger.debug(f"Found plantit.yaml in {owner}/{repository['name']}/{branch['name']}")

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
    async def list_connectable_repos_by_owner_async(self,
                                                    owner: str,
                                                    token: Optional[str] = None,
                                                    timeout: Optional[int] = None) -> List[dict]:
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
        }
        async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
            workflows = []
            owned_repos = await self.list_repositories_async(owner, token)
            for repository in owned_repos:
                branches = await self.list_repo_branches_async(owner, repository['name'], token)
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
    async def list_user_organizations_async(self,
                                            username: str,
                                            token: Optional[str] = None,
                                            timeout: Optional[int] = None) -> List[dict]:
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
