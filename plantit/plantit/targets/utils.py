from typing import List

from plantit.targets.models import Target, TargetRole, TargetPolicy, TargetTask, TargetAccessRequest


def map_target_task(task: TargetTask):
    return {
        'name': task.name,
        'description': task.description,
        'command': task.command,
        'crontab': str(task.crontab).rpartition("(")[0].strip(),
        'enabled': task.enabled,
        'last_run': task.last_run_at
    }


def map_target(target: Target, role: TargetRole = None, policies: List[TargetPolicy] = None, access_requests: List[TargetAccessRequest] = None):
    tasks = TargetTask.objects.filter(target=target)
    mapped = {
        'name': target.name,
        'description': target.description,
        'hostname': target.hostname,
        'pre_commands': target.pre_commands,
        'max_walltime': target.max_walltime,
        'max_mem': target.max_mem,
        'max_cores': target.max_cores,
        'max_processes': target.max_processes,
        'queue': target.queue,
        'project': target.project,
        'workdir': target.workdir,
        'executor': target.executor,
        'disabled': target.disabled,
        'public': target.public,
        'gpu': target.gpu,
        'tasks': [map_target_task(task) for task in tasks],
        'logo': target.logo
    }

    if role is not None:
        mapped['role'] = role.value.lower()

    if policies is not None:
        mapped['policies'] = [{
            'user': policy.user.username,
            'role': str(policy.role.value)
        } for policy in policies]

    if access_requests is not None:
        mapped['access_requests'] = [{
            'user': request.user.username,
            'created': request.created.isoformat(),
            'granted': request.granted
        } for request in access_requests]

    return mapped


def run_workdir_clean_task_name(target: str, run_id: str):
    return f"Clean working directory for run {run_id} on {target}"
