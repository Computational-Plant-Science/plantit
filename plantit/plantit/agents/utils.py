import json
import logging
from typing import List

from asgiref.sync import sync_to_async, async_to_sync
from django.contrib.auth.models import User

from plantit.agents.models import Agent, AgentRole, AgentAccessPolicy, AgentTask, AgentAccessRequest
from plantit.redis import RedisClient

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


@sync_to_async
def map_agent_async(agent: Agent, user: User = None):
    return map_agent(agent, user)


def map_agent(agent: Agent, user: User = None) -> dict:
    tasks = AgentTask.objects.filter(agent=agent)
    redis = RedisClient.get()
    users_authorized = agent.users_authorized.all() if agent.users_authorized is not None else []
    workflows_authorized = agent.workflows_authorized.all() if agent.workflows_authorized is not None else []
    workflows_blocked = agent.workflows_blocked.all() if agent.workflows_blocked is not None else []
    mapped = {
        'name': agent.name,
        'guid': agent.guid,
        'role': AgentRole.admin if user is not None and agent.user == user else AgentRole.guest,
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
        'authentication': agent.authentication,
        'users_authorized': [json.loads(redis.get(f"users/{user.username}")) for user in users_authorized if user is not None],
        'workflows_authorized': [json.loads(redis.get(f"workflows/{workflow.repo_owner}/{workflow.repo_name}")) for workflow in workflows_authorized],
        'workflows_blocked': [json.loads(redis.get(f"workflows/{workflow.repo_owner}/{workflow.repo_name}")) for workflow in workflows_blocked]
    }

    if agent.user is not None: mapped['user'] = agent.user.username
    return mapped


def run_workdir_clean_task_name(agent: str, run_id: str):
    return f"Clean {agent} run {run_id} working directory"


def has_virtual_memory(agent: Agent):
    return agent.header_skip == '--mem'


@sync_to_async
def get_agent_user(agent: Agent):
    return agent.user
