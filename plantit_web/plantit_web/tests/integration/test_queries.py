from uuid import uuid4
from pprint import pprint

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

import plantit_web.workflows as q
import plantit_web.statistics

from plantit_web.users.models import Profile
from plantit_web.tasks.models import Task
from plantit_web.tokens import TerrainToken


class QueriesTests(TestCase):
    def setUp(self):
        user = User.objects.create(
            username='wbonelli', first_name="Wes", last_name="Bonelli")
        profile = Profile.objects.create(
            user=user,
            github_username='w-bonelli',
            github_token=settings.GITHUB_TOKEN,
            cyverse_access_token=TerrainToken.get(),
            institution='University of Georgia',
            first_login=True
        )
        guid = str(uuid4())

        # created second user
        user2 = User.objects.create(
            username='okn69169', first_name="Obi", last_name="Nnaduruaku")
        profile2 = Profile.objects.create(
            user=user2,
            github_username='obi9999n',
            github_token=settings.GITHUB_TOKEN,
            cyverse_access_token=TerrainToken.get(),
            institution='Georgia Tech',
            first_login=True
        )
        # task = Task.objects.create(
        #     guid=guid,
        #     name=guid,
        #     user=user,
        #     workflow=workflow,
        #     workflow_owner=repo_owner,
        #     workflow_name=repo_name,
        #     workflow_branch=repo_branch,
        #     agent=agent,
        #     status=TaskStatus.CREATED,
        #     created=now,
        #     updated=now,
        #     due_time=due_time,
        #     token=binascii.hexlify(os.urandom(20)).decode())

    def test_get_workflows_usage_timeseries(self):
        user = User.objects.get(username='wbonelli')
        series = plantit.statistics.get_workflows_usage_timeseries(user)
        pprint(series)

    # same test with different user
    def test_get_workflows_usage_timeseries2(self):
        user = User.objects.get(username='okn69169')
        series = plantit.statistics.get_workflows_usage_timeseries(user)
        pprint(series)

    def test_get_institutions_cache_miss(self):
        institutions = plantit.statistics.get_institutions(invalidate=True)
        self.assertTrue('university of georgia' in institutions)
        self.assertTrue(institutions['university of georgia']['count'] == 1)
        self.assertTrue(institutions['university of georgia']
                        ['geocode']['text'] == 'University of Georgia')

    # same test with different institution
    def test_get_institutions_cache_miss2(self):
        institutions = plantit.statistics.get_institutions(invalidate=True)
        self.assertTrue('georgia tech' in institutions)
        self.assertTrue(institutions['georgia tech']['count'] == 1)
        self.assertTrue(institutions['georgia tech']
                        ['geocode']['text'] == 'Georgia Tech')

    def test_get_institutions_cache_hit(self):
        institutions = plantit.statistics.get_institutions()

        # TODO
        # self.assertTrue('university of georgia' in institutions)
        # self.assertTrue(institutions['university of georgia']['count'] == 1)
        # self.assertTrue(institutions['university of georgia']['geocode']['text'] == 'University of Georgia')
