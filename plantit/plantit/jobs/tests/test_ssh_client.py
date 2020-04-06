from django.test import TestCase
from ..ssh_client import SSHClient


class SSHClientTests(TestCase):

    def test_connection (self):
        ssh = SSHClient('ssh', 22, 'root', 'root')
        with ssh:
            self.assertTrue(ssh.client.get_transport() is not None)
            self.assertTrue(ssh.client.get_transport().is_active())
