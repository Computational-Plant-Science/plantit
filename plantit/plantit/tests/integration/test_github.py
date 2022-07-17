from django.conf import settings
from django.test import TestCase

from plantit.github import GitHubClient, AsyncGitHubClient


class GithubTests(TestCase):
    def test_list_user_organizations(self):
        client = GitHubClient(settings.GITHUB_TOKEN)
        institutions = client.list_user_organizations('w-bonelli', settings.GITHUB_TOKEN)

        self.assertGreater(len(institutions), 0)
        self.assertTrue('Computational-Plant-Science' in [i['login'] for i in institutions])

    async def test_list_user_organizations_async(self):
        client = AsyncGitHubClient(settings.GITHUB_TOKEN)
        institutions = await client.list_user_organizations_async('w-bonelli', settings.GITHUB_TOKEN)

        self.assertGreater(len(institutions), 0)
        self.assertTrue('Computational-Plant-Science' in [i['login'] for i in institutions])
