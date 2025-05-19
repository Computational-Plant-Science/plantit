import os
import requests


class TerrainToken:
    __token = None

    @staticmethod
    def get():
        if TerrainToken.__token is not None:
            return TerrainToken.__token

        cyverse_username = os.environ.get('CYVERSE_USERNAME', None)
        cyverse_password = os.environ.get('CYVERSE_PASSWORD', None)

        if cyverse_username is None: raise ValueError("Missing environment variable 'CYVERSE_USERNAME'")
        if cyverse_password is None: raise ValueError("Missing environment variable 'CYVERSE_PASSWORD'")

        response = requests.get('https://de.cyverse.org/terrain/token', auth=(cyverse_username, cyverse_password))
        response.raise_for_status()

        TerrainToken.__token = response.json()['access_token']
        return TerrainToken.__token
