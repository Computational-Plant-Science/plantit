from uuid import uuid4
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from plantit.agents.models import Agent
from plantit.miappe.models import Investigation, Study
from plantit.users.models import Profile
from plantit.tokens import TerrainToken
from plantit.task_lifecycle import create_immediate_task


class TaskLifecycleTests(TestCase):
    def setUp(self):
        user = User.objects.create(
            username='wbonelli',
            first_name="Wes",
            last_name="Bonelli")
        profile = Profile.objects.create(
            user=user,
            github_username='w-bonelli',
            github_token=settings.GITHUB_TOKEN,
            cyverse_access_token=TerrainToken.get(),
            institution='University of Georgia',
            first_login=True
        )
        agent = Agent.objects.create(
            name='Sandbox'
        )
        project = Investigation.objects.create(
            owner=user,
            title='Test Project'
        )
        study = Study.objects.create(
            investigation=project,
            title='Test Study'
        )

    def test_create_immediate_task(self):
        config = {
            'type': 'now',
            'guid': str(uuid4()),
            'name': 'Test Task',
            'agent': 'Sandbox',
            'tags': [
                'testing',
                '123'
            ],
            'workflow': {
                'name': 'Hello world',
                'image': 'docker://alpine',
                'commands': 'echo "Hello, world"',
                'output': {
                    'to': '/my/collection/path'
                }
            },
            'repo': {
                'owner': 'Computational-Plant-Science',
                'name': 'plantit-example-hello-world',
                'branch': 'master'
            },
            'miappe': {
                'project': 'Test Project',
                'study': 'Test Study'
            }

        }
        user = User.objects.get(username='wbonelli')
        task = create_immediate_task(user, config)
        agent = Agent.objects.get(name='Sandbox')
        project = Investigation.objects.get(title='Test Project')
        study = Study.objects.get(title='Test Study')

        self.assertEqual(user, task.user)
        self.assertEqual(task.agent, agent)
        self.assertEqual(task.project, project)
        self.assertEqual(task.study, study)
        self.assertEqual(task.transfer_path, '/my/collection/path')
        tags = [str(tag) for tag in task.tags.all()]
        self.assertEqual(len(tags), 2)
        self.assertTrue('testing' in tags)
        self.assertTrue('123' in tags)
