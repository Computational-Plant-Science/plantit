from os import environ
from pprint import pprint

from django.test import TestCase

import plantit.github as github


token = environ.get('GH_TOKEN')
if not token:
    token = environ.get('GITHUB_TOKEN')


username = environ.get('GH_USERNAME')
if not username:
    username = environ.get('GITHUB_USERNAME')

if not (username and token):
    raise ValueError(f"Need github username and auth token")


class GithubTests(TestCase):
    async def test_list_user_organizations(self):
        institutions = await github.list_user_organizations(username, token)

        self.assertGreater(len(institutions), 0)
        self.assertTrue('Computational-Plant-Science' in [inst['login'] for inst in institutions])
