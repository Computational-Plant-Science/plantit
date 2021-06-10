import logging
import subprocess
from os.path import join
from typing import List

from django.conf import settings
from pathlib import Path

from plantit.agents.models import Agent, AgentRole, AgentAccessPolicy, AgentTask, AgentAccessRequest

logger = logging.getLogger(__name__)


def map_agent_task(task: AgentTask):
    return {
        'name': task.name,
        'description': task.description,
        'command': task.command,
        'crontab': str(task.crontab).rpartition("(")[0].strip(),
        'enabled': task.enabled,
        'last_run': task.last_run_at
    }


def map_agent(
        agent: Agent,
        role: AgentRole = None,
        policies: List[AgentAccessPolicy] = None,
        requests: List[AgentAccessRequest] = None):
    tasks = AgentTask.objects.filter(agent=agent)
    mapped = {
        'name': agent.name,
        'guid': agent.guid,
        'description': agent.description,
        'hostname': agent.hostname,
        'pre_commands': agent.pre_commands,
        'max_walltime': agent.max_walltime,
        'max_mem': agent.max_mem,
        'max_cores': agent.max_cores,
        'max_processes': agent.max_processes,
        'queue': agent.queue,
        'project': agent.project,
        'workdir': agent.workdir,
        'executor': agent.executor,
        'disabled': agent.disabled,
        'public': agent.public,
        'gpu': agent.gpu,
        'tasks': [map_agent_task(task) for task in tasks],
        'logo': agent.logo,
        'authentication': agent.authentication
    }

    if agent.user is not None:
        mapped['user'] = agent.user.username

    if role is not None:
        mapped['role'] = role.value.lower()

    if policies is not None:
        mapped['policies'] = [{
            'user': policy.user.username,
            'role': str(policy.role.value)
        } for policy in policies]
    else:
        mapped['policies'] = []

    if requests is not None:
        mapped['access_requests'] = [{
            'user': request.user.username,
            'created': request.created.isoformat(),
            'granted': request.granted
        } for request in requests]
    else:
        mapped['access_requests'] = []

    return mapped


def run_workdir_clean_task_name(agent: str, run_id: str):
    return f"Clean {agent} run {run_id} working directory"


def get_public_key_path(owner: str) -> Path:
    keys_path = Path(settings.AGENT_KEYS)
    owner_keys_path = Path(f"{keys_path.absolute()}/{owner}")
    owner_keys_path.mkdir(exist_ok=True, parents=True)
    return Path(join(owner_keys_path, f"{owner}_id_rsa.pub"))


def get_private_key_path(owner: str) -> Path:
    keys_path = Path(settings.AGENT_KEYS)
    owner_keys_path = Path(f"{keys_path.absolute()}/{owner}")
    owner_keys_path.mkdir(exist_ok=True, parents=True)
    return Path(join(owner_keys_path, f"{owner}_id_rsa"))


def create_keypair(owner: str, overwrite: bool = False) -> str:
    """
    Creates an RSA-protected SSH keypair for the user and returns the public key (or gets the public key if a keypair already exists).
    To overwrite a pre-existing keypair, use the `invalidate` argument.

    Args:
        owner: The user (CyVerse/Django username) to create a keypair for.
        overwrite: Whether to overwrite an existing keypair.

    Returns: The path to the newly created public key.
    """
    public_key_path = get_public_key_path(owner)
    private_key_path = get_private_key_path(owner)

    if public_key_path.is_file():
        if overwrite:
            logger.info(f"Keypair for {owner} already exists, overwriting")
            public_key_path.unlink()
            private_key_path.unlink(missing_ok=True)
        else:
            logger.info(f"Keypair for {owner} already exists")
    else:
        subprocess.run(f"ssh-keygen -b 2048 -t rsa -f {private_key_path} -N \"\"", shell=True)
        logger.info(f"Created keypair for {owner}")

    with open(public_key_path, 'r') as key:
        return key.readlines()[0]
