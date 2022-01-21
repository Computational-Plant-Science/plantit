import subprocess
import traceback
import logging
from typing import List

from paramiko import SSHException
from requests import RequestException, ReadTimeout, Timeout, HTTPError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from plantit.agents.models import Agent
from plantit.ssh import SSH, execute_command
from plantit.keypairs import get_user_private_key_path

logger = logging.getLogger(__name__)


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
def is_healthy(agent: Agent) -> (bool, List[str]):
    """
    Checks agent health

    Args:
        agent: the agent

    Returns: True if the agent was successfully reached, otherwise false.
    """

    output = []
    try:
        ssh = SSH(host=agent.hostname, port=agent.port, username=agent.username, pkey=str(get_user_private_key_path(agent.user.username)))

        try:
            with ssh:
                logger.info(f"Checking agent {agent.name}'s health")
                for line in execute_command(ssh=ssh, precommand=':', command=f"pwd", directory=agent.workdir):
                    logger.info(line)
                    output.append(line)
                logger.info(f"Agent {agent.name} healthcheck succeeded")
                return True, output
        except SSHException as e:
            if 'not found in known_hosts' in str(e):
                # add the hostname to known_hosts and retry
                subprocess.run(f"ssh-keyscan {agent.hostname} >> /code/config/ssh/known_hosts", shell=True)
                with ssh:
                    logger.info(f"Checking agent {agent.name}'s health")
                    for line in execute_command(ssh=ssh, precommand=':', command=f"pwd", directory=agent.workdir):
                        logger.info(line)
                        output.append(line)
                    logger.info(f"Agent {agent.name} healthcheck succeeded")
                    return True, output
            else:
                raise e
    except:
        msg = f"Agent {agent.name} healthcheck failed:\n{traceback.format_exc()}"
        logger.warning(msg)
        output.append(msg)
        return False, output