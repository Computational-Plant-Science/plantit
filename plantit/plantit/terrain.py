import json
import asyncio
import logging
import multiprocessing
import pprint
from contextlib import closing
from multiprocessing import Pool
from os import environ
from os.path import basename, join, isfile, isdir
from typing import List, Tuple

import httpx
import requests
from requests import RequestException, ReadTimeout, Timeout
from requests.auth import HTTPBasicAuth
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from pycyapi.exceptions import Unauthorized, BadRequest, BadResponse, NotFound
from plantit.utils.misc import list_local_files

logger = logging.getLogger(__name__)


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout)))
def refresh_tokens(username: str, refresh_token: str) -> (str, str):
    logger.debug(f"Refreshing CyVerse tokens for user {username}")
    response = requests.post("https://kc.cyverse.org/auth/realms/CyVerse/protocol/openid-connect/token", data={
        'grant_type': 'refresh_token',
        'client_id': environ.get('CYVERSE_CLIENT_ID'),
        'client_secret': environ.get('CYVERSE_CLIENT_SECRET'),
        'refresh_token': refresh_token,
        'redirect_uri': environ.get('CYVERSE_REDIRECT_URL')},
                             auth=HTTPBasicAuth(username, environ.get('CYVERSE_CLIENT_SECRET')))

    if response.status_code == 400:
        raise Unauthorized('Unauthorized for KeyCloak token endpoint')
    elif response.status_code != 200:
        raise BadResponse(f"Bad response from KeyCloak token endpoint:\n{response.json()}")

    content = response.json()
    if 'access_token' not in content or 'refresh_token' not in content:
        raise BadRequest(f"Missing params on token response, expected 'access_token' and 'refresh_token' but got:\n{pprint.pprint(content)}")

    return content['access_token'], content['refresh_token']


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout)))
async def get_dirs_async(paths: List[str], token: str, timeout: int = 15):
    logger.debug(f"Listing data store directories: {', '.join(paths)}")
    urls = [f"https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path={path}" for path in paths]
    headers = {
        "Authorization": f"Bearer {token}",
    }
    async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
        tasks = [client.get(url).json() for url in urls]
        results = await asyncio.gather(*tasks)
        return results
