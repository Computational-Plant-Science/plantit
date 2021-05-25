from typing import List

import requests
from requests import RequestException, ReadTimeout, Timeout, HTTPError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type


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
def path_exists(path, token):
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