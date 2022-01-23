from urllib.parse import quote_plus

import httpx
from django.conf import settings
from requests import RequestException, ReadTimeout, Timeout, HTTPError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
async def get_institution(name: str, token: str) -> dict:
    """
    Queries the Mapbox geocoding API for information about an institution.

    Args:
        name: The institution name
        token: The authentication token

    Returns:
        Potential matches for the institution with geocoding info
    """

    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{quote_plus(name)}.json?access_token={token}"
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
