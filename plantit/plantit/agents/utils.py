import logging
from typing import List

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
