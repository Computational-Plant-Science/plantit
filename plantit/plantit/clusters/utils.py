from typing import List

from plantit.clusters.models import Cluster, ClusterRole, ClusterAccessPolicy, ClusterTask, ClusterAccessRequest


def map_cluster_task(task: ClusterTask):
    return {
        'name': task.name,
        'description': task.description,
        'command': task.command,
        'crontab': str(task.crontab).rpartition("(")[0].strip(),
        'enabled': task.enabled,
        'last_run': task.last_run_at
    }


def map_cluster(cluster: Cluster, role: ClusterRole = None, policies: List[ClusterAccessPolicy] = None, requests: List[ClusterAccessRequest] = None):
    tasks = ClusterTask.objects.filter(cluster=cluster)
    mapped = {
        'name': cluster.name,
        'description': cluster.description,
        'hostname': cluster.hostname,
        'pre_commands': cluster.pre_commands,
        'max_walltime': cluster.max_walltime,
        'max_mem': cluster.max_mem,
        'max_cores': cluster.max_cores,
        'max_processes': cluster.max_processes,
        'queue': cluster.queue,
        'project': cluster.project,
        'workdir': cluster.workdir,
        'executor': cluster.executor,
        'disabled': cluster.disabled,
        'public': cluster.public,
        'gpu': cluster.gpu,
        'tasks': [map_cluster_task(task) for task in tasks],
        'logo': cluster.logo
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


def run_workdir_clean_task_name(cluster: str, run_id: str):
    return f"Clean working directory for run {run_id} on {cluster}"
