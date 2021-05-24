from typing import List

from plantit.resources.models import Resource, ResourceRole, ResourceAccessPolicy, ResourceTask, ResourceAccessRequest


def map_resource_task(task: ResourceTask):
    return {
        'name': task.name,
        'description': task.description,
        'command': task.command,
        'crontab': str(task.crontab).rpartition("(")[0].strip(),
        'enabled': task.enabled,
        'last_run': task.last_run_at
    }


def map_resource(
        resource: Resource,
        role: ResourceRole = None,
        policies: List[ResourceAccessPolicy] = None,
        requests: List[ResourceAccessRequest] = None):
    tasks = ResourceTask.objects.filter(resource=resource)
    mapped = {
        'name': resource.name,
        'description': resource.description,
        'hostname': resource.hostname,
        'pre_commands': resource.pre_commands,
        'max_walltime': resource.max_walltime,
        'max_mem': resource.max_mem,
        'max_cores': resource.max_cores,
        'max_processes': resource.max_processes,
        'queue': resource.queue,
        'project': resource.project,
        'workdir': resource.workdir,
        'executor': resource.executor,
        'disabled': resource.disabled,
        'public': resource.public,
        'gpu': resource.gpu,
        'tasks': [map_resource_task(task) for task in tasks],
        'logo': resource.logo
    }

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


def run_workdir_clean_task_name(resource: str, run_id: str):
    return f"Clean working directory for run {run_id} on {resource}"
