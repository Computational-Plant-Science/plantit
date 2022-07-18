import json
from pathlib import Path

from django.contrib.auth.models import User

from plantit.agents.models import Agent, AgentRole
from plantit.datasets.models import DatasetAccessPolicy
from plantit.miappe.models import Study, Investigation
from plantit.misc.models import NewsUpdate
from plantit.notifications.models import Notification
from plantit.redis import RedisClient
from plantit.tasks.models import Task, DelayedTask, RepeatingTask, TriggeredTask
from plantit.users.models import Migration, ManagedFile
from plantit.utils.tasks import get_task_orchestrator_log_file_path, has_output_target


def agent_to_dict(agent: Agent, username: str = None) -> dict:
    role = AgentRole.admin if username is not None and agent.user.username == username else AgentRole.guest
    users_authorized = agent.users_authorized.all() if agent.users_authorized is not None else []
    users_authorized = [user.username for user in users_authorized if user is not None]
    mapped = {
        'name': agent.name,
        'guid': agent.guid,
        'role': role,
        'description': agent.description,
        'hostname': agent.hostname,
        'username': agent.username,
        'pre_commands': agent.pre_commands,
        'max_walltime': agent.max_walltime,
        'max_mem': agent.max_mem,
        'max_cores': agent.max_cores,
        'max_processes': agent.max_processes,
        'queue': agent.queue,
        'workdir': agent.workdir,
        'executor': agent.scheduler,
        'disabled': agent.disabled,
        'public': agent.public,
        'gpus': agent.gpus,
        'logo': agent.logo,
        'is_healthy': agent.is_healthy,
        'users_authorized': users_authorized,
    }

    if agent.user is not None: mapped['user'] = agent.user.username
    return mapped


def dataset_access_policy_to_dict(policy: DatasetAccessPolicy):
    return {
        'owner': policy.owner.username,
        'guest': policy.guest.username,
        'path': policy.path,
        'role': policy.role.value
    }


def task_to_dict(task: Task) -> dict:
    orchestrator_log_file_path = get_task_orchestrator_log_file_path(task)
    if Path(orchestrator_log_file_path).is_file():
        with open(orchestrator_log_file_path, 'r') as log:
            orchestrator_logs = [line.strip() for line in log.readlines()[-int(1000000):]]
    else:
        orchestrator_logs = []

    # try:
    #     AgentAccessPolicy.objects.get(user=task.user, agent=task.agent, role__in=[AgentRole.admin, AgentRole.guest])
    #     can_restart = True
    # except:
    #     can_restart = False

    results = RedisClient.get().get(f"results/{task.guid}")

    return {
        # 'can_restart': can_restart,
        'guid': task.guid,
        'status': task.status,
        'owner': task.user.username,
        'name': task.name,
        'project': {
            'title': task.project.title,
            'owner': task.project.owner.username,
            'description': task.project.description
        } if task.project is not None else None,
        'study': {
            'title': task.study.title,
            'description': task.study.description
        } if task.study is not None else None,
        'work_dir': task.workdir,
        'orchestrator_logs': orchestrator_logs,
        'agent': agent_to_dict(task.agent) if task.agent is not None else None,
        'created': task.created.isoformat(),
        'updated': task.updated.isoformat(),
        'completed': task.completed.isoformat() if task.completed is not None else None,
        'due_time': None if task.due_time is None else task.due_time.isoformat(),
        'cleanup_time': None if task.cleanup_time is None else task.cleanup_time.isoformat(),
        'workflow_owner': task.workflow_owner,
        'workflow_name': task.workflow_name,
        'workflow_branch': task.workflow_branch,
        'workflow_image_url': task.workflow_image_url,
        'input_path': task.workflow['input']['path'] if 'input' in task.workflow else None,
        'output_path': task.workflow['output']['to'] if ('output' in task.workflow and 'to' in task.workflow['output']) else None,
        'tags': [str(tag) for tag in task.tags.all()],
        'is_complete': task.is_complete,
        'is_success': task.is_success,
        'is_failure': task.is_failure,
        'is_cancelled': task.is_cancelled,
        'is_timeout': task.is_timeout,
        'result_previews_loaded': task.previews_loaded,
        'result_transfer': has_output_target(task),
        'results_retrieved': task.results_retrieved,
        'results_transferred': task.results_transferred,
        'cleaned_up': task.cleaned_up,
        'transferred': task.transferred,
        'transfer_path': task.transfer_path,
        'output_files': json.loads(results) if results is not None else [],
        'job_id': task.job_id,
        'job_status': task.job_status,
        # 'job_walltime': task.job_consumed_walltime,
        'delayed_id': task.delayed_id,
        'repeating_id': task.repeating_id,
        'triggered_id': task.triggered_id
    }


def delayed_task_to_dict(task: DelayedTask) -> dict:
    return {
        # 'agent': agent_to_dict(task.agent),
        'name': task.name,
        'eta': task.eta,
        'enabled': task.enabled,
        'interval': {
            'every': task.interval.every,
            'period': task.interval.period
        },
        'last_run': task.last_run_at,
        'workflow_owner': task.workflow_owner,
        'workflow_name': task.workflow_name,
        'workflow_branch': task.workflow_branch,
        'workflow_image_url': task.workflow_image_url,

    }


def repeating_task_to_dict(task: RepeatingTask):
    return {
        # 'agent': agent_to_dict(task.agent),
        'name': task.name,
        'eta': task.eta,
        'interval': {
            'every': task.interval.every,
            'period': task.interval.period
        },
        'enabled': task.enabled,
        'last_run': task.last_run_at,
        'workflow_owner': task.workflow_owner,
        'workflow_name': task.workflow_name,
        'workflow_branch': task.workflow_branch,
        'workflow_image_url': task.workflow_image_url,
    }


def triggered_task_to_dict(task: TriggeredTask):
    return {
        # 'agent': agent_to_dict(task.agent),
        'name': task.name,
        'eta': task.eta,
        'path': task.path,
        'modified': task.modified.isoformat(),
        'interval': {
            'every': task.interval.every,
            'period': task.interval.period
        },
        'enabled': task.enabled,
        'last_run': task.last_run_at,
        'workflow_owner': task.workflow_owner,
        'workflow_name': task.workflow_name,
        'workflow_branch': task.workflow_branch,
        'workflow_image_url': task.workflow_image_url,
    }


def study_to_dict(study: Study, project: Investigation) -> dict:
    team = [person_to_dict(person, 'Researcher') for person in study.team.all()]
    return {
        'project_title': project.title,
        'project_owner': project.owner.username,
        'guid': study.guid,
        'title': study.title,
        'description': study.description,
        'start_date': study.start_date,
        'end_date': study.end_date,
        'contact_institution': study.contact_institution,
        'country': study.country,
        'site_name': study.site_name if study.site_name != '' else None,
        'latitude': study.latitude,
        'longitude': study.longitude,
        'altitude': study.altitude,
        'altitude_units': study.altitude_units,
        'experimental_design_description': study.experimental_design_description if study.experimental_design_description != '' else None,
        'experimental_design_type': study.experimental_design_type if study.experimental_design_type != '' else None,
        'experimental_design_map': study.experimental_design_map if study.experimental_design_map != '' else None,
        'observation_unit_level_hierarchy': study.observation_unit_level_hierarchy if study.observation_unit_level_hierarchy != '' else None,
        'observation_unit_description': study.observation_unit_description if study.observation_unit_description != '' else None,
        'growth_facility_description': study.growth_facility_description if study.growth_facility_description != '' else None,
        'growth_facility_type': study.growth_facility_type if study.growth_facility_type != '' else None,
        'cultural_practices': study.cultural_practices if study.cultural_practices != '' else None,
        'team': team,
    }


def project_to_dict(project: Investigation) -> dict:
    studies = [study_to_dict(study, project) for study in Study.objects.select_related().filter(investigation=project)]
    team = [person_to_dict(person, 'Researcher') for person in project.team.all()]
    return {
        'guid': project.guid,
        'owner': project.owner.username,
        'title': project.title,
        'description': project.description,
        'submission_date': project.submission_date,
        'public_release_date': project.public_release_date,
        'associated_publication': project.associated_publication,
        'studies': studies,
        'team': team,
    }


def notification_to_dict(notification: Notification) -> dict:
    return {
        'id': notification.guid,
        'username': notification.user.username,
        'created': notification.created.isoformat(),
        'message': notification.message,
        'read': notification.read,
    }


def person_to_dict(user: User, role: str) -> dict:
    return {
        'name': f"{user.first_name} {user.last_name}",
        'email': user.email,
        'username': user.username,
        'affiliation': user.profile.institution,
        'role': role,
    }


def migration_to_dict(migration: Migration) -> dict:
    return {
        'started': None if migration.started is None else migration.started.isoformat(),
        'completed': None if migration.completed is None else migration.completed.isoformat(),
        'target_path': migration.target_path,
        'num_files': migration.num_files,
        'num_metadata': migration.num_metadata,
        'num_outputs': migration.num_outputs,
        'num_logs': migration.num_logs,
        'uploaded': ManagedFile.objects.filter(migration=migration).count()
    }


def managed_file_to_dict(file: ManagedFile) -> dict:
    return {
        'id': file.id,
        'name': file.name,
        'nfs_path': file.nfs_path,
        'path': file.path,
        'type': file.type,
        'folder': file.folder,
        'orphan': file.orphan,
        'missing': file.missing,
        'uploaded': file.uploaded,
        'entity_id': file.entity_id,
        'collection_entity_id': file.collection_entity_id
    }


def update_to_dict(update: NewsUpdate):
    return {
        'created': update.created.isoformat(),
        'content': update.content
    }