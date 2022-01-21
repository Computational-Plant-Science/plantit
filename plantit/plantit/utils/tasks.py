import os
import traceback
from datetime import timedelta, datetime
from os.path import join
from typing import List

from dateutil import parser
from django.utils import timezone

from plantit.tasks.models import Task, BindMount


def format_bind_mount(workdir: str, bind_mount: BindMount) -> str:
    return bind_mount['host_path'] + ':' + bind_mount['container_path'] if bind_mount['host_path'] != '' else workdir + ':' + bind_mount[
        'container_path']


def parse_bind_mount(workdir: str, bind_mount: str) -> BindMount:
    split = bind_mount.rpartition(':')
    return BindMount(host_path=split[0], container_path=split[2]) if len(split) > 0 else BindMount(host_path=workdir, container_path=bind_mount)


def get_task_orchestrator_log_file_name(task: Task):
    return f"plantit.{task.guid}.log"


def get_task_orchestrator_log_file_path(task: Task):
    return join(os.environ.get('TASKS_LOGS'), get_task_orchestrator_log_file_name(task))


def get_task_agent_log_file_name(task: Task):
    return f"{task.guid}.{task.agent.name.lower()}.log"


def get_task_agent_log_file_path(task: Task):
    return join(os.environ.get('TASKS_LOGS'), get_task_agent_log_file_name(task))


def get_task_scheduler_log_file_name(task: Task):
    return f"plantit.{task.job_id}.out"


def get_task_scheduler_log_file_path(task: Task):
    return join(os.environ.get('TASKS_LOGS'), get_task_scheduler_log_file_name(task))


def get_included_by_name(task: Task) -> List[str]:
    included_by_name = (
        (task.workflow['output']['include']['names'] if 'names' in task.workflow['output'][
            'include'] else [])) if 'output' in task.workflow else []
    included_by_name.append(f"{task.guid}.zip")  # zip file
    if not task.agent.launcher: included_by_name.append(f"{task.guid}.{task.agent.name.lower()}.log")
    included_by_name.append(f"plantit.{task.job_id}.out")
    included_by_name.append(f"plantit.{task.job_id}.err")

    return included_by_name


def get_included_by_pattern(task: Task) -> List[str]:
    included_by_pattern = (task.workflow['output']['include']['patterns'] if 'patterns' in task.workflow['output'][
        'include'] else []) if 'output' in task.workflow else []
    included_by_pattern.append('.out')
    included_by_pattern.append('.err')
    included_by_pattern.append('.zip')

    return included_by_pattern


def should_transfer_results(task: Task) -> bool:
    return 'output' in task.workflow['config'] and 'to' in task.workflow['config']['output']


def parse_task_walltime(walltime) -> timedelta:
    time_split = walltime.split(':')
    time_hours = int(time_split[0])
    time_minutes = int(time_split[1])
    time_seconds = int(time_split[2])
    return timedelta(hours=time_hours, minutes=time_minutes, seconds=time_seconds)


def parse_task_job_id(line: str) -> str:
    try:
        return str(int(line.replace('Submitted batch job', '').strip()))
    except:
        raise Exception(f"Failed to parse job ID from '{line}'\n{traceback.format_exc()}")


def parse_task_time(data: dict) -> datetime:
    time_str = data['time']
    time = parser.isoparse(time_str)
    return time


def parse_task_eta(data: dict) -> (datetime, int):
    delay_value = data['delayValue']
    delay_units = data['delayUnits']

    if delay_units == 'Seconds':
        seconds = int(delay_value)
    elif delay_units == 'Minutes':
        seconds = int(delay_value) * 60
    elif delay_units == 'Hours':
        seconds = int(delay_value) * 60 * 60
    elif delay_units == 'Days':
        seconds = int(delay_value) * 60 * 60 * 24
    else:
        raise ValueError(f"Unsupported delay units (expected: Seconds, Minutes, Hours, or Days)")

    now = timezone.now()
    eta = now + timedelta(seconds=seconds)

    return eta, seconds


def parse_time_limit_seconds(time):
    time_limit = time['limit']
    time_units = time['units']
    seconds = time_limit
    if time_units == 'Days':
        seconds = seconds * 60 * 60 * 24
    elif time_units == 'Hours':
        seconds = seconds * 60 * 60
    elif time_units == 'Minutes':
        seconds = seconds * 60
    return seconds
