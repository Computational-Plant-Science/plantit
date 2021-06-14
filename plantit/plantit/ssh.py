import logging
from typing import List

import paramiko
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from plantit.utils import clean_html

logger = logging.getLogger(__name__)


class SSH:
    """
    Wraps a paramiko client with either password or key authentication. Preserves `with` statement usability.
    """

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
def execute_command(ssh: SSH, precommand: str, command: str, directory: str = None, allow_stderr: bool = False) -> List[str]:
    """
    Executes the given command on the given SSH connection. This method is a generator and will yield any output produced line by line.

    Args:
        ssh: The SSH client.
        precommand: Commands to prepend to the primary command.
        command: The command.
        directory: Directory to run the command in.
        allow_stderr: Whether to permit `stderr` output (by default an error is thrown).

    Returns:

    """
    full_command = f"{precommand} && {command}"
    if directory is not None: full_command = f"cd {directory} && {full_command}"

    logger.info(f"Executing command on '{ssh.host}': {full_command}")
    stdin, stdout, stderr = ssh.client.exec_command(full_command, get_pty=True)
    stdin.close()

    for line in iter(lambda: stdout.readline(2048), ""):
        clean = clean_html(line)
        # logger.info(f"Received stdout from '{ssh.host}': '{clean}'")
        yield clean

    errors = []
    for line in iter(lambda: stderr.readline(2048), ""):
        clean = clean_html(line)
        # Dask occasionally returns messages like 'distributed.worker - WARNING - Heartbeat to scheduler failed'
        if 'WARNING' not in clean: errors.append(clean)
        logger.warning(f"Received stderr from '{ssh.host}': '{clean}'")
        yield clean

    if stdout.channel.recv_exit_status() != 0: raise Exception(f"Received non-zero exit status from '{ssh.host}'")
    elif not allow_stderr and len(errors) > 0: raise Exception(f"Received stderr: {errors}")
