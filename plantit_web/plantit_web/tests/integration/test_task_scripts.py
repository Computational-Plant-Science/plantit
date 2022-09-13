from uuid import uuid4
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from plantit_web.agents.models import Agent
from plantit_web.miappe.models import Investigation, Study
from plantit_web.users.models import Profile
from plantit_web.tokens import TerrainToken
from plantit_web.task_lifecycle import create_immediate_task
from plantit_web.task_scripts import compose_singularity_invocation


class TaskLifecycleTests(TestCase):
    def test_compose_task_singularity_command_shell(self):
        commands = compose_singularity_invocation(
            work_dir='/work/dir',
            image='docker://alpine',
            commands='echo "Hello, world!"',
            shell='bash'
        )
        commands = [c.strip() for c in commands]

        self.assertTrue(
            'SINGULARITYENV_WORKDIR="/work/dir" singularity exec --home /work/dir docker://alpine bash -c \'echo "Hello, world!"\'' in commands)

        commands = compose_singularity_invocation(
            work_dir='/work/dir',
            image='docker://alpine',
            commands='echo "Hello, world!"',
            shell='sh'
        )
        commands = [c.strip() for c in commands]

        self.assertTrue(
            'SINGULARITYENV_WORKDIR="/work/dir" singularity exec --home /work/dir docker://alpine sh -c \'echo "Hello, world!"\'' in commands)

        commands = compose_singularity_invocation(
            work_dir='/work/dir',
            image='docker://alpine',
            commands='echo "Hello, world!"',
        )
        commands = [c.strip() for c in commands]

        self.assertTrue(
            'SINGULARITYENV_WORKDIR="/work/dir" singularity exec --home /work/dir docker://alpine sh -c \'echo "Hello, world!"\'' in commands)
