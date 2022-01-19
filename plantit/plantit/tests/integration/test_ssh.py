import unittest
from django.test import TestCase

from plantit.ssh import SSH


@unittest.skip("until sandbox container is back")
class SSHClientTests(TestCase):
    """
    Requires a container `sandbox` running alongside the container under test, as in the configuration in `docker-compose.dev.yml`

    """
    def test_password_connection(self):
        ssh = SSH('sandbox', 22, 'root', 'root')
        with ssh:
            self.assertTrue(ssh.client.get_transport() is not None)
            self.assertTrue(ssh.client.get_transport().is_active())

    def test_key_connection(self):
        ssh = SSH('sandbox', 22, 'root')
        with ssh:
            self.assertTrue(ssh.client.get_transport() is not None)
            self.assertTrue(ssh.client.get_transport().is_active())

    def test_command(self):
        ssh = SSH('sandbox', 22, 'root', 'root')
        with ssh:
            stdin, stdout, stderr = ssh.client.exec_command('pwd')
            self.assertEqual('/root\n', stdout.readlines()[0])


