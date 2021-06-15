import json
import logging
import pprint
from os import environ
from typing import List

import requests
from requests import RequestException, ReadTimeout, Timeout, HTTPError
from requests.auth import HTTPBasicAuth
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

logger = logging.getLogger(__name__)


# TODO use asyncx


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
    if response.status_code == 401 or response.status_code == 403:
        raise ValueError('Invalid token')
    else:
        content = response.json()
        if username in content:
            return content[username]
        else:
            raise ValueError(f"User {username} has no CyVerse profile")


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
def path_exists(path, token):
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
