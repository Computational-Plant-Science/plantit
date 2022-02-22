import requests

from requests import RequestException, ReadTimeout, Timeout, HTTPError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
def image_exists(name, owner=None, tag=None):
    url = f"https://hub.docker.com/v2/repositories/{owner if owner is not None else 'library'}/{name}/"
    if tag is not None:
        url += f"tags/{tag}/"
    response = requests.get(url)
    try:
        content = response.json()
        if 'user' not in content and 'name' not in content:
            return False
        if content['name'] != tag and content['name'] != name and content['user'] != (owner if owner is not None else 'library'):
            return False
        return True
    except:
        return False


def parse_image_components(value):
    container_split = value.split('#', 1)[0].strip().split('/')  # get rid of comments first
    print(container_split)
    container_name = container_split[-1]
    container_owner = None if container_split[-2] == '' else container_split[-2]
    if ':' in container_name:
        container_name_split = container_name.split(":")
        container_name = container_name_split[0]
        container_tag = container_name_split[1]
    else:
        container_tag = None

    return container_owner, container_name, container_tag