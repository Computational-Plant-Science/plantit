from pprint import pprint

from django.conf import settings
from django.test import TestCase

import plantit.github as github


class GithubTests(TestCase):
    async def test_list_user_organizations(self):
        institutions = await github.list_user_organizations('w-bonelli', settings.GITHUB_TOKEN)

        self.assertGreater(len(institutions), 0)
        self.assertTrue('Computational-Plant-Science' in [inst['login'] for inst in institutions])
