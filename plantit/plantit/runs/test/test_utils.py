from django.test import TestCase

from plantit.runs.ssh import SSH
from plantit.runs.utils import execute_command


class UtilsTests(TestCase):
    def test_execute_command(self):
        ssh = SSH('sandbox', 22, 'root', 'root')
        with ssh:
            lines = execute_command(ssh_client=ssh, pre_command=':', command='pwd', directory='/root', allow_stderr=False)
            self.assertEqual('/root\n', lines[0])

    def test_execute_command_with_pre_command(self):
        ssh = SSH('sandbox', 22, 'root', 'root')
        with ssh:
            lines = execute_command(ssh_client=ssh, pre_command='pwd', command='pwd', directory='/root', allow_stderr=False)
            self.assertEqual('/root\n', lines[0])
            self.assertEqual('/root\n', lines[1])