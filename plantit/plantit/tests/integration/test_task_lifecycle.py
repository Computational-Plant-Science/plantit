from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from plantit.agents.models import Agent
from plantit.task_lifecycle import create_immediate_task
from plantit.tokens import TerrainToken
from plantit.users.models import Profile


class TaskLifecycleTests(TestCase):
    def setUp(self):
        user = User.objects.create(username='wbonelli', first_name="Wes", last_name="Bonelli")
        profile = Profile.objects.create(
            user=user,
            github_username='w-bonelli',
            github_token=settings.GITHUB_TOKEN,
            cyverse_access_token=TerrainToken.get(),
            institution='University of Georgia',
            first_login=True
        )
        # agent = Agent.objects.create()

    def test_create_task(self):
        pass

    def test_create_immediate_task(self):
        config = {

        }
        user = User.objects.get(username='wbonelli')
        task = create_immediate_task(user, config)

        self.assertEqual(user, task.user)
        self.assertEqual()