import fileinput
import os
import sys
import logging
from os import environ
from os.path import join
from pathlib import Path
from typing import List

from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer

from plantit.keypairs import get_user_private_key_path
from plantit.queries import get_task_user, task_to_dict
from plantit.ssh import SSH
from plantit.tasks.models import Task
from plantit.utils.tasks import get_task_orchestrator_log_file_path, get_task_scheduler_log_file_name, get_task_scheduler_log_file_path, \
    get_task_agent_log_file_name, get_task_agent_log_file_path

logger = logging.getLogger(__name__)


def get_task_ssh_client(task: Task) -> SSH:
    return SSH(
        host=task.agent.hostname,
        port=task.agent.port,
        username=task.agent.username,
        pkey=str(get_user_private_key_path(task.agent.user.username)))


async def push_task_channel_event(task: Task):
    user = await get_task_user(task)
    await get_channel_layer().group_send(f"{user.username}", {
        'type': 'task_event',
        'task': await sync_to_async(task_to_dict)(task),
    })


def log_task_orchestrator_status(task: Task, messages: List[str]):
    log_path = get_task_orchestrator_log_file_path(task)
    with open(log_path, 'a') as log:
        for message in messages:
            logger.info(f"[{task.user.username}'s task {task.guid}] {message}")
            log.write(f"{message}\n")


def get_remote_logs(log_file_name: str, log_file_path: str, task: Task, ssh: SSH, sftp):
    work_dir = join(task.agent.workdir, task.workdir)
    log_path = join(work_dir, log_file_name)
    # cmd = f"test -e {log_path} && echo exists"
    # logger.info(f"Using command: {cmd}")
    # stdin, stdout, stderr = ssh.client.exec_command(cmd)
    # if not stdout.read().decode().strip() == 'exists':
    #     logger.warning(f"Agent log file {log_file_name} does not exist")
    try:
        with open(log_file_path, 'a+') as log_file:
            sftp.chdir(work_dir)
            sftp.get(log_file_name, log_file.name)
    except:
        logger.warning(f"Agent log file {log_file_name} does not exist")

    # obfuscate Docker auth info before returning logs to the user
    docker_username = environ.get('DOCKER_USERNAME', None)
    docker_password = environ.get('DOCKER_PASSWORD', None)
    lines = 0
    for line in fileinput.input([log_file_path], inplace=True):
        if docker_username in line.strip():
            line = line.strip().replace(docker_username, '*' * 7, 1)
        if docker_password in line.strip():
            line = line.strip().replace(docker_password, '*' * 7)
        lines += 1
        sys.stdout.write(line)

    logger.info(f"Retrieved {lines} line(s) from {log_file_name}")


def get_task_remote_logs(task: Task, ssh: SSH):
    with ssh:
        with ssh.client.open_sftp() as sftp:
            # orchestrator_log_file_name = get_task_orchestrator_log_file_name(task)
            # orchestrator_log_file_path = get_task_orchestrator_log_file_path(task)
            # get_remote_logs(orchestrator_log_file_name, orchestrator_log_file_path, task, ssh, sftp)

            scheduler_log_file_name = get_task_scheduler_log_file_name(task)
            scheduler_log_file_path = get_task_scheduler_log_file_path(task)
            get_remote_logs(scheduler_log_file_name, scheduler_log_file_path, task, ssh, sftp)

            if not task.agent.launcher:
                agent_log_file_name = get_task_agent_log_file_name(task)
                agent_log_file_path = get_task_agent_log_file_path(task)
                get_remote_logs(agent_log_file_name, agent_log_file_path, task, ssh, sftp)


def remove_task_orchestration_logs(task: Task):
    log_path = get_task_orchestrator_log_file_path(task)
    os.remove(log_path)


def get_agent_log_file_contents(task: Task) -> List[str]:
    agent_log_file_path = get_task_agent_log_file_path(task)
    if not task.agent.launcher and Path(agent_log_file_path).is_file():
        with open(agent_log_file_path, 'r') as log:
            agent_logs = [line.strip() for line in log.readlines()[-int(1000000):]]
    else:
        agent_logs = []

    return agent_logs


def get_scheduler_log_file_contents(task: Task) -> List[str]:
    scheduler_log_file_path = get_task_scheduler_log_file_path(task)
    if Path(scheduler_log_file_path).is_file():
        with open(scheduler_log_file_path, 'r') as log:
            scheduler_logs = [line.strip() + "\n" for line in log.readlines()[-int(1000000):]]
    else:
        scheduler_logs = []

    return scheduler_logs