import logging
from typing import List

import paramiko
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from plantit.utils import clean_html

logger = logging.getLogger(__name__)


class SSH:
    def __init__(self, host: str, port: int, username: str, password: str = None, pkey: str = None):
        self.client = None
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.pkey = pkey
        self.logger = logging.getLogger(__name__)

    def __enter__(self):
        client = paramiko.SSHClient()
        client.load_host_keys('../config/ssh/known_hosts')
        client.set_missing_host_key_policy(paramiko.RejectPolicy())

        if self.password is not None:
            client.connect(self.host, self.port, self.username, self.password)
        elif self.pkey is not None:
            # key = paramiko.RSAKey.from_private_key_file('../config/ssh/id_rsa')
            key = paramiko.RSAKey.from_private_key_file(self.pkey)
            client.connect(hostname=self.host, port=self.port, username=self.username, pkey=key)
        else:
            raise ValueError(f"No authentication strategy provided")

        self.client = client

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.close()


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type())
def execute_command(ssh_client: SSH, pre_command: str, command: str, directory: str = None, allow_stderr: bool = False) -> List[str]:
    full_command = f"{pre_command} && {command}"
    if directory is not None: full_command = f"cd {directory} && {full_command}"
    output = []
    errors = []

    logger.info(f"Executing command on '{ssh_client.host}': {full_command}")
    stdin, stdout, stderr = ssh_client.client.exec_command(full_command, get_pty=True)
    stdin.close()

    for line in iter(lambda: stdout.readline(2048), ""):
        clean = clean_html(line)
        logger.info(f"Received stdout from '{ssh_client.host}': '{clean}'")
        yield clean

    for line in iter(lambda: stderr.readline(2048), ""):
        clean = clean_html(line)

        # Dask occasionally returns messages like 'distributed.worker - WARNING - Heartbeat to scheduler failed'
        if 'WARNING' not in clean: errors.append(clean)

        logger.warning(f"Received stderr from '{ssh_client.host}': '{clean}'")
        yield clean

    if stdout.channel.recv_exit_status() != 0:
        raise Exception(f"Received non-zero exit status from '{ssh_client.host}'")
    elif not allow_stderr and len(errors) > 0:
        raise Exception(f"Received stderr: {errors}")
