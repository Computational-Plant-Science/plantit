from uuid import uuid4
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from plantit.agents.models import Agent
from plantit.miappe.models import Investigation, Study
from plantit.users.models import Profile
from plantit.tokens import TerrainToken
from plantit.task_lifecycle import create_immediate_task
from plantit.task_scripts import compose_task_singularity_command


class TaskLifecycleTests(TestCase):
    def test_compose_task_singularity_command_shell_wrapper(self):
        command = compose_task_singularity_command(
            work_dir='/work/dir',
            image='docker://alpine',
            command='echo "Hello, world!"',
            shell_wrapper='bash'
        )

        self.assertTrue(
            'SINGULARITYENV_WORKDIR="/work/dir" singularity exec --home /work/dir docker://alpine bash -c \'echo "Hello, world!"\'' in command)

        command = compose_task_singularity_command(
            work_dir='/work/dir',
            image='docker://alpine',
            command='echo "Hello, world!"',
            shell_wrapper='sh'
        )

        self.assertTrue(
            'SINGULARITYENV_WORKDIR="/work/dir" singularity exec --home /work/dir docker://alpine sh -c \'echo "Hello, world!"\'' in command)

        command = compose_task_singularity_command(
            work_dir='/work/dir',
            image='docker://alpine',
            command='echo "Hello, world!"',
        )

        self.assertTrue(
            'SINGULARITYENV_WORKDIR="/work/dir" singularity exec --home /work/dir docker://alpine echo "Hello, world!"' in command)
