import json
import asyncio
import logging
import multiprocessing
import pprint
from contextlib import closing
from multiprocessing import Pool
from os import environ, listdir
from os.path import basename, join, isfile, isdir
from typing import List, Tuple

import httpx
import requests
from requests import RequestException, ReadTimeout, Timeout, HTTPError
from requests.auth import HTTPBasicAuth
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

logger = logging.getLogger(__name__)


def list_files(path,
               include_patterns=None,
               include_names=None,
               exclude_patterns=None,
               exclude_names=None):
    # gather all files
    all_paths = [join(path, file) for file in listdir(path) if isfile(join(path, file))]

    # add files matching included patterns
    included_by_pattern = [pth for pth in all_paths if any(
        pattern.lower() in pth.lower() for pattern in include_patterns)] if include_patterns is not None else all_paths

    # add files included by name
    included_by_name = ([pth for pth in all_paths if pth.rpartition('/')[2] in [name for name in include_names]] \
                            if include_names is not None else included_by_pattern) + \
                       [pth for pth in all_paths if pth in [name for name in include_names]] \
        if include_names is not None else included_by_pattern

    # gather only included files
    included = list(set(included_by_pattern + included_by_name))

    # remove files matched excluded patterns
    excluded_by_pattern = [name for name in included if all(pattern.lower() not in name.lower() for pattern in
                                                            exclude_patterns)] if exclude_patterns is not None else included

    # remove files excluded by name
    excluded_by_name = [pattern for pattern in excluded_by_pattern if pattern.split('/')[
        -1] not in exclude_names] if exclude_names is not None else excluded_by_pattern

    return excluded_by_name


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
def get_profile(username: str, access_token: str) -> dict:
    response = requests.get(
        f"https://de.cyverse.org/terrain/secured/user-info?username={username}",
        headers={'Authorization': f"Bearer {access_token}"})
    response.raise_for_status()
    content = response.json()
    if username in content: return content[username]
    else: return None


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
def refresh_tokens(username: str, refresh_token: str) -> (str, str):
    response = requests.post("https://kc.cyverse.org/auth/realms/CyVerse/protocol/openid-connect/token", data={
        'grant_type': 'refresh_token',
        'client_id': environ.get('CYVERSE_CLIENT_ID'),
        'client_secret': environ.get('CYVERSE_CLIENT_SECRET'),
        'refresh_token': refresh_token,
        'redirect_uri': environ.get('CYVERSE_REDIRECT_URL')},
                             auth=HTTPBasicAuth(username, environ.get('CYVERSE_CLIENT_SECRET')))

    if response.status_code == 400:
        raise ValueError('Unauthorized for KeyCloak token endpoint')
    elif response.status_code != 200:
        raise ValueError(f"Bad response from KeyCloak token endpoint:\n{response.json()}")

    content = response.json()
    if 'access_token' not in content or 'refresh_token' not in content:
        raise ValueError(f"Missing params on token response, expected 'access_token' and 'refresh_token' but got:\n{pprint.pprint(content)}")

    return content['access_token'], content['refresh_token']


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
def list_dir(path: str, token: str) -> List[str]:
    with requests.get(
            f"https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path={path}",
            headers={'Authorization': f"Bearer {token}"}) as response:
        if response.status_code == 500 and response.json()['error_code'] == 'ERR_DOES_NOT_EXIST':
            raise ValueError(f"Path {path} does not exist")

        response.raise_for_status()
        content = response.json()
        files = content['files']
        return [file['path'] for file in files]


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
async def get_dirs(paths: List[str], token: str, timeout: int = 15) -> List[dict]:
    urls = [f"https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path={path}" for path in paths]
    headers = {
        "Authorization": f"Bearer {token}",
    }
    async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
        tasks = [client.get(url).json() for url in urls]
        results = await asyncio.gather(*tasks)
        return results


async def create_dir(path: str, token: str, timeout: int = 15):
    headers = {
        "Authorization": f"Bearer {token}",
    }
    async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
        response = await client.post("https://de.cyverse.org/terrain/secured/filesystem/directory/create", data=json.dumps({'path': path}))
        response.raise_for_status()


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
async def share_dir(dir: dict, token: str, timeout: int = 15):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json;charset=utf-8"
    }
    async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
        response = await client.post("https://de.cyverse.org/terrain/secured/share", data=json.dumps(dir))
        response.raise_for_status()


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
async def unshare_dir(path: str, token: str, timeout: int = 15):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": 'application/json;charset=utf-8'
    }
    async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
        response = await client.post("https://de.cyverse.org/terrain/secured/unshare",
                                     data=json.dumps({'unshare': [{'user': path, 'paths': [path]}]}))
        response.raise_for_status()


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
def get_file(path: str, token: str) -> List[str]:
    with requests.post(
            "https://de.cyverse.org/terrain/secured/filesystem/stat",
            data=json.dumps({'paths': [path]}),
            headers={'Authorization': f"Bearer {token}", "Content-Type": 'application/json;charset=utf-8'}) as response:
        if response.status_code == 500 and response.json()['error_code'] == 'ERR_DOES_NOT_EXIST':
            raise ValueError(f"Path {path} does not exist")
        elif response.status_code == 400:
            pprint.pprint(response.json())

        response.raise_for_status()
        content = response.json()
        return content['paths'][path]


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
def path_exists(path, token) -> Tuple[bool, str]:
    response = requests.get(f"https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path={path}",
                            headers={"Authorization": f"Bearer {token}"})
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
                    return False, None
                elif 'error_code' in up_content:
                    print(f"Error: {up_content['error_code']}")
                    return False, None
            elif 'files' not in up_content:
                print(f"Directory '{base}' does not exist")
                return False, None
            elif len(up_content['files']) != 1:
                print(f"Multiple files found in directory '{base}' matching name '{file}'")
                return False, None
            elif up_content['files'][0]['label'] != file:
                print(f"File '{file}' does not exist in directory '{base}'")
                return False, None
            else:
                input_type = 'file'
        else:
            return False, None
    return True, input_type


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
def push_file(from_path: str, to_prefix: str, token: str):
    print(f"Uploading '{from_path}' to '{to_prefix}'")
    with open(from_path, 'rb') as file:
        with requests.post(f"https://de.cyverse.org/terrain/secured/fileio/upload?dest={to_prefix}",
                           headers={'Authorization': f"Bearer {token}"},
                           files={'file': (basename(from_path), file, 'application/octet-stream')}) as response:
            if response.status_code == 500 and response.json()['error_code'] == 'ERR_EXISTS':
                print(f"File '{join(to_prefix, basename(file.name))}' already exists, skipping upload")
            else:
                response.raise_for_status()


def push_dir(from_path: str,
             to_prefix: str,
             include_patterns: List[str] = None,
             include_names: List[str] = None,
             exclude_patterns: List[str] = None,
             exclude_names: List[str] = None):
    is_file = isfile(from_path)
    is_dir = isdir(from_path)

    if not (is_dir or is_file):
        raise FileNotFoundError(f"Local path '{from_path}' does not exist")
    elif is_dir:
        from_paths = list_files(from_path, include_patterns, include_names, exclude_patterns, exclude_names)
        print(f"Uploading directory '{from_path}' with {len(from_paths)} file(s) to '{to_prefix}'")
        with closing(Pool(processes=multiprocessing.cpu_count())) as pool:
            pool.starmap(push_file, [(path, to_prefix) for path in [str(p) for p in from_paths]])
    elif is_file:
        push_file(from_path, to_prefix)
    else:
        raise ValueError(f"Remote path '{to_prefix}' is a file; specify a directory path instead")
