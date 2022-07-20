import fileinput
import logging
import os
import sys
from os.path import join
from typing import List

from plantit.keypairs import get_user_private_key_path
from plantit.ssh import SSH
from plantit.tasks.models import Task
from plantit.utils.tasks import get_task_orchestrator_log_file_path

logger = logging.getLogger(__name__)


def log_task_status(task: Task, messages: List[str]):
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
    # docker_username = environ.get('DOCKER_USERNAME', None)
    # docker_password = environ.get('DOCKER_PASSWORD', None)
    lines = 0
    for line in fileinput.input([log_file_path], inplace=True):
        # if docker_username in line.strip():
        #     line = line.strip().replace(docker_username, '*' * 7, 1)
        # if docker_password in line.strip():
        #     line = line.strip().replace(docker_password, '*' * 7)
        lines += 1
        sys.stdout.write(line)

    logger.info(f"Retrieved {lines} line(s) from {log_file_name}")


def remove_task_orchestration_logs(task: Task):
    log_path = get_task_orchestrator_log_file_path(task)
    os.remove(log_path)


def get_task_ssh_client(task: Task) -> SSH:
    return SSH(
        host=task.agent.hostname,
        port=task.agent.port,
        username=task.agent.username,
        pkey=str(get_user_private_key_path(task.agent.user.username)))