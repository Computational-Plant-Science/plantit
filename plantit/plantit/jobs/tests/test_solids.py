from dagster import execute_solid
from django.test import TestCase
import tempfile
from ..dagster.solids import *
from ..ssh import SSHOptions


class SolidsTests(TestCase):

    def test_sftp_upload_text(self):
        text = "Hello, world!"
        remote_path = "/file"
        ssh_options = SSHOptions('cluster', 22, 'root')

        result = execute_solid(
            sftp_upload_file,
            input_values={
                'ssh_options': ssh_options,
                'text': text,
                'remote_path': remote_path
            })

        self.assertTrue(result.success)

        ssh = SSH.from_options(ssh_options)
        with ssh:
            stdin, stdout, stderr = ssh.client.exec_command(f"[[ -f {remote_path} ]] || printf 'fail'")
            self.assertTrue(len(stdout.readlines()) == 0)
            ssh.client.exec_command(f"rm {remote_path}")

    def test_sftp_upload_file(self):
        local_file = tempfile.NamedTemporaryFile()
        local_path = local_file.name
        remote_path = "/file"
        ssh_options = SSHOptions('cluster', 22, 'root')

        result = execute_solid(
            sftp_upload_file,
            input_values={
                'ssh_options': ssh_options,
                'file': LocalFileHandle(local_path),
                'remote_path': remote_path
            })

        self.assertTrue(result.success)

        ssh = SSH.from_options(ssh_options)
        with ssh:
            stdin, stdout, stderr = ssh.client.exec_command(f"[[ -f {remote_path} ]] || printf 'fail'")
            self.assertTrue(len(stdout.readlines()) == 0)
            ssh.client.exec_command(f"rm {remote_path}")

    def test_ssh_execute(self):
        ssh_options = SSHOptions('cluster', 22, 'root')
        command = "ls /"

        result = execute_solid(
            ssh_execute,
            input_values={
                'ssh_options': ssh_options,
                'command': command,
            })

        self.assertTrue(result.success)
        actual = result.output_value()

        ssh = SSH.from_options(ssh_options)
        with ssh:
            stdin, stdout, stderr = ssh.client.exec_command(command)
            expected = stdout.readlines() + stderr.readlines()
            self.assertTrue(len(expected) == len(actual) and sorted(expected) == sorted(actual))

    def test_upload_workflow_collection(self):
        pass

    def test_upload_workflow_definition(self):
        pass

    def test_upload_workflow_parameters(self):
        pass

    def test_execute_workflow(self):
        pass
