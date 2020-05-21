import paramiko
from dagster import DagsterType
from django.conf import settings


class SSHOptions:
    def __init__(self, host: str, port: int, username: str, password: str = None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password


DagsterSSHOptions = DagsterType(
    name='SSHOptions',
    type_check_fn=lambda _, value: isinstance(value, SSHOptions),
    description='SSH connection options'
)


class SSH:
    def __init__(self, host: str, port: int, username: str, password: str = None):
        self.client = None
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    @classmethod
    def from_options(cls, options: SSHOptions):
        return cls(options.host, options.port, options.username, options.password)

    def __enter__(self):
        client = paramiko.SSHClient()
        client.load_host_keys('../config/ssh/known_hosts')

        if getattr(settings, 'DEBUG', False):
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        else:
            client.set_missing_host_key_policy(paramiko.RejectPolicy())

        if self.password:
            client.connect(self.host, self.port, self.username, self.password)
        else:
            key = paramiko.RSAKey.from_private_key_file('../config/ssh/id_rsa')
            client.connect(self.host, self.port, self.username, pkey=key)

        self.client = client

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.close()

