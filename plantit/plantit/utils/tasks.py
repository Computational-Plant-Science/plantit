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


def get_output_included_names(task: Task) -> List[str]:
    try:
        included = list(task.workflow['output']['include']['names'])
    except:
        included = []

    # default inclusions: scheduler log files and zip file
    included.append(f"{task.guid}.zip")
    included.append(f"plantit.{task.job_id}.out")
    included.append(f"plantit.{task.job_id}.err")

    return included


def get_output_included_patterns(task: Task) -> List[str]:
    try:
        return list(task.workflow['output']['include']['patterns'])
    except:
        return []


def has_output_target(task: Task) -> bool:
    """
    Determines whether the given task has a target CyVerse collection to transfer results to

    Args:
        task: The task

    Returns: True if the task has a target collection, otherwise false
    """

    try:
        target = task.workflow['output']['to']
        return isinstance(target, str) and target != ''
    except:
        return False


def parse_task_walltime(walltime: str) -> timedelta:
    """
    Converts a walltime string (format HH:MM:SS) to a timedelta

    Args:
        walltime: The walltime string

    Returns: The timedelta

    """
    time_split = walltime.split(':')

    # if we don't have 3 elements, or if they can't be parsed as ints, the walltime string is malformed
    error = ValueError(f"Malformed walltime string (required format: HH:MM:SS): {walltime}")
    if len(time_split) != 3: raise error
    try:
        time_hours = int(time_split[0])
        time_minutes = int(time_split[1])
        time_seconds = int(time_split[2])
    except ValueError:
        raise error

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
    """
    Parses the dictionary for the delayed or repeating task's ETA (datetime and seconds from now)

    Args:
        data: The dictionary, including 'delay' and 'units' attributes

    Returns: The ETA (datetime) and seconds from now

    """
    delay = data.get('delay', None)
    units = data.get('units', None)

    if delay is None: raise ValueError(f"Missing 'value' attribute")
    if units is None: units = 'seconds'  # use seconds by default

    # web UI might send capitalized units
    units = units.lower()

    try: delay = int(delay)
    except: raise ValueError(f"Failed to parse 'delay' as integer")

    # convert delay to seconds
    if units == 'seconds': seconds = delay
    elif units == 'minutes': seconds = delay * 60
    elif units == 'hours': seconds = delay * 60 * 60
    elif units == 'days': seconds = delay * 60 * 60 * 24
    else: raise ValueError(f"Unsupported units (expected: seconds, minutes, hours, or days)")

    # calculate time task should start
    now = timezone.now()
    eta = now + timedelta(seconds=seconds)

    return eta, seconds


def parse_task_time_limit(data: dict):
    """
    Parses the dictionary for the task's time limit in total seconds

    Args:
        data: The dictionary, including 'limit' and 'units' attributes

    Returns: The time limit (in seconds)

    """
    limit = data.get('limit', None)
    units = data.get('units', None)

    if limit is None: raise ValueError(f"Missing 'limit' attribute")
    if units is None: units = 'seconds'  # use seconds by default

    # web UI might send capitalized units
    units = units.lower()

    try: limit = int(limit)
    except: raise ValueError(f"Failed to parse 'limit' as integer")

    # convert limit to seconds
    if units == 'seconds': seconds = limit
    elif units == 'minutes': seconds = limit * 60
    elif units == 'hours': seconds = limit * 60 * 60
    elif units == 'days': seconds = limit * 60 * 60 * 24
    else: raise ValueError(f"Unsupported units (expected: seconds, minutes, hours, or days)")

    return seconds


def parse_task_miappe_info(data: dict):
    try:
        project = data['project']
        if 'study' in data:
            study = data['study']
            return project, study
        else:
            return project, None
    except:
        return None, None
