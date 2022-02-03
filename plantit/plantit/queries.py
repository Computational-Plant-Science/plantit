import asyncio
import concurrent.futures
import json
import logging
from collections import Counter, namedtuple, OrderedDict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple

import jwt
import numpy as np
import pandas as pd
from asgiref.sync import sync_to_async, async_to_sync
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Count
from django.utils import timezone

import plantit.terrain as terrain
import plantit.mapbox as mapbox
from plantit import github as github
from plantit import loess as loess
from plantit.redis import RedisClient
from plantit.agents.models import Agent, AgentRole
from plantit.miappe.models import Investigation, Study
from plantit.notifications.models import Notification
from plantit.misc.models import NewsUpdate
from plantit.datasets.models import DatasetAccessPolicy
from plantit.tasks.models import Task, DelayedTask, RepeatingTask, TaskCounter, TaskStatus
from plantit.users.models import Profile
from plantit.utils.misc import del_none
from plantit.utils.tasks import get_task_orchestrator_log_file_path, has_output_target

logger = logging.getLogger(__name__)


def get_project_workflows(project: Investigation):
    redis = RedisClient.get()
    workflows = [wf for wf in [json.loads(redis.get(key)) for key in redis.scan_iter(match='workflows/*')] if
                 'projects' in wf['config'] and project.guid in wf['config']['projects']]
    return workflows


async def refresh_online_users_workflow_cache():
    users = await sync_to_async(User.objects.all)()
    online = await sync_to_async(filter_online)(users)
    logger.info(f"Refreshing workflow cache for {len(online)} online user(s)")
    for user in online:
        profile = await sync_to_async(Profile.objects.get)(user=user)
        await refresh_user_workflow_cache(profile.github_username)


async def refresh_user_workflow_cache(github_username: str):
    if github_username is None or github_username == '': raise ValueError(f"No GitHub username provided")

    try:
        profile = await sync_to_async(Profile.objects.get)(github_username=github_username)
        user = await get_profile_user(profile)
    except MultipleObjectsReturned:
        logger.warning(f"Multiple users bound to Github user {github_username}!")
        return
    except:
        logger.warning(f"Github user {github_username} does not exist")
        return

    # scrape GitHub to synchronize repos and workflow config
    profile = await sync_to_async(Profile.objects.get)(user=user)
    workflows = await github.list_connectable_repos_by_owner(github_username, profile.github_token)

    # update the cache, first removing workflows that no longer exist
    redis = RedisClient.get()
    removed = 0
    updated = 0
    added = 0
    old_keys = [key.decode('utf-8') for key in redis.scan_iter(match=f"workflows/{github_username}/*")]
    new_keys = [f"workflows/{github_username}/{wf['repo']['name']}/{wf['branch']['name']}" for wf in workflows]
    for old_key in old_keys:
        if old_key not in new_keys:
            logger.debug(f"Removing user workflow {old_key}")
            removed += 1
            redis.delete(old_key)
        else:
            logger.debug(f"Updating user workflow {old_key}")
            updated += 1

    # ...then adding/updating the workflows we just scraped
    for wf in workflows:
        key = f"workflows/{github_username}/{wf['repo']['name']}/{wf['branch']['name']}"
        if key not in old_keys:
            logger.debug(f"Adding user workflow {key}")
            added += 1
        redis.set(key, json.dumps(del_none(wf)))

    redis.set(f"workflows_updated/{github_username}", timezone.now().timestamp())
    logger.info(
        f"{len(workflows)} workflow(s) now in GitHub user's {github_username}'s workflow cache (added {added}, updated {updated}, removed {removed})")


async def refresh_online_user_orgs_workflow_cache():
    users = await sync_to_async(User.objects.all)()
    online = await sync_to_async(filter_online)(users)
    for user in online:
        profile = await sync_to_async(Profile.objects.get)(user=user)
        github_organizations = await get_user_github_organizations(user)
        logger.info(f"Refreshing workflow cache for online user {user.username}'s {len(online)} organizations")
        for org in github_organizations:
            await refresh_org_workflow_cache(org['login'], profile.github_token)


async def refresh_org_workflow_cache(org_name: str, github_token: str):
    # scrape GitHub to synchronize repos and workflow config
    workflows = await github.list_connectable_repos_by_org(org_name, github_token)

    # update the cache, first removing workflows that no longer exist
    redis = RedisClient.get()
    removed = 0
    updated = 0
    added = 0
    old_keys = [key.decode('utf-8') for key in redis.scan_iter(match=f"workflows/{org_name}/*")]
    new_keys = [f"workflows/{org_name}/{wf['repo']['name']}/{wf['branch']['name']}" for wf in workflows]
    for old_key in old_keys:
        if old_key not in new_keys:
            logger.debug(f"Removing org workflow {old_key}")
            removed += 1
            redis.delete(old_key)
        else:
            logger.debug(f"Updating org workflow {old_key}")
            updated += 1

    # ...then adding/updating the workflows we just scraped
    for wf in workflows:
        key = f"workflows/{org_name}/{wf['repo']['name']}/{wf['branch']['name']}"
        if key not in old_keys:
            logger.debug(f"Adding org workflow {key}")
            added += 1
        redis.set(key, json.dumps(del_none(wf)))

    redis.set(f"workflows_updated/{org_name}", timezone.now().timestamp())
    logger.info(
        f"{len(workflows)} workflow(s) now in GitHub organization {org_name}'s workflow cache (added {added}, updated {updated}, removed {removed})")


def list_public_workflows() -> List[dict]:
    redis = RedisClient.get()
    workflows = [wf for wf in [json.loads(redis.get(key)) for key in redis.scan_iter(match='workflows/*')] if
                 'public' in wf['config'] and wf['config']['public']]
    return workflows


def list_user_workflows(owner: str) -> List[dict]:
    redis = RedisClient.get()
    return [json.loads(redis.get(key)) for key in redis.scan_iter(match=f"workflows/{owner}/*")]


async def get_workflow(
        owner: str,
        name: str,
        branch: str,
        github_token: str,
        cyverse_token: str,
        invalidate: bool = False) -> dict:
    redis = RedisClient.get()
    last_updated = redis.get(f"workflows_updated/{owner}")
    workflow = redis.get(f"workflows/{owner}/{name}/{branch}")

    if last_updated is None or workflow is None or invalidate:
        bundle = await github.get_repo_bundle(owner, name, branch, github_token, cyverse_token)
        workflow = {
            'config': bundle['config'],
            'repo': bundle['repo'],
            'validation': bundle['validation'],
            'branch': branch
        }
        redis.set(f"workflows/{owner}/{name}/{branch}", json.dumps(del_none(workflow)))
        return workflow
    else:
        return json.loads(workflow)


def list_users(invalidate: bool = False) -> List[dict]:
    redis = RedisClient.get()
    updated = redis.get(f"users_updated")

    # repopulate if empty or invalidation requested
    if updated is None or len(list(redis.scan_iter(match=f"users/*"))) == 0 or invalidate:
        refresh_user_cache()
    else:
        age = (datetime.now() - datetime.fromtimestamp(float(updated)))
        age_secs = age.total_seconds()
        max_secs = (int(settings.USERS_REFRESH_MINUTES) * 60)

        # otherwise only if stale
        if age_secs > max_secs:
            logger.info(f"User cache is stale ({age_secs}s old, {age_secs - max_secs}s past limit), repopulating")
            refresh_user_cache()

    return [json.loads(redis.get(key)) for key in redis.scan_iter(match=f"users/*")]


def refresh_user_cache():
    logger.info(f"Refreshing user cache")
    redis = RedisClient.get()
    for user in list(User.objects.all().exclude(profile__isnull=True)):
        bundle = get_user_bundle(user)
        redis.set(f"users/{user.username}", json.dumps(bundle))
    RedisClient.get().set(f"users_updated", timezone.now().timestamp())


def has_github_info(profile: Profile):
    return profile.github_token is not None and \
           profile.github_token != '' and \
           profile.github_username is not None and \
           profile.github_username != ''


def get_user_bundle(user: User):
    profile = Profile.objects.get(user=user)
    if not has_github_info(profile):
        return {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
    else:
        redis = RedisClient.get()
        cached = redis.get(f"users/{user.username}")
        if cached is not None: return json.loads(cached)
        github_profile = async_to_sync(get_user_github_profile)(user)
        github_organizations = async_to_sync(get_user_github_organizations)(user)
        bundle = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'github_username': profile.github_username,
            'github_profile': github_profile,
            'github_organizations': github_organizations,
        } if 'login' in github_profile else {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
        redis.set(f"users/{user.username}", json.dumps(bundle))
        return bundle


def agent_to_dict(agent: Agent, username: str = None) -> dict:
    users_authorized = agent.users_authorized.all() if agent.users_authorized is not None else []
    mapped = {
        'name': agent.name,
        'guid': agent.guid,
        'role': AgentRole.admin if username is not None and agent.user.username == username else AgentRole.guest,
        'description': agent.description,
        'hostname': agent.hostname,
        'username': agent.username,
        'pre_commands': agent.pre_commands,
        'max_walltime': agent.max_walltime,
        'max_mem': agent.max_mem,
        'max_cores': agent.max_cores,
        'max_processes': agent.max_processes,
        'queue': agent.queue,
        # 'project': agent.project,  # don't want to reveal this to end users
        'workdir': agent.workdir,
        'executor': agent.scheduler,
        'disabled': agent.disabled,
        'public': agent.public,
        'gpus': agent.gpus,
        # 'tasks': [agent_task_to_dict(task) for task in tasks],
        'logo': agent.logo,
        'is_healthy': agent.is_healthy,
        'users_authorized': [get_user_bundle(user) for user in users_authorized if user is not None],
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
        'inputs_detected': task.inputs_detected,
        'inputs_downloaded': task.inputs_downloaded,
        'inputs_submitted': task.inputs_submitted,
        'inputs_completed': task.inputs_completed,
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
        'job_walltime': task.job_consumed_walltime,
        'delayed_id': task.delayed_id,
        'repeating_id': task.repeating_id
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
        'dataset_paths': study.dataset_paths if study.dataset_paths is not None else []
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
        'workflows': get_project_workflows(project)
    }


@sync_to_async
def list_user_projects(user: User):
    return list(user.project_teams.all()) + list(Investigation.objects.filter(owner=user))


def get_user_cyverse_profile(user: User) -> dict:
    profile = terrain.get_profile(user.username, user.profile.cyverse_access_token)
    if profile is None: raise ValueError(f"User {user.username} has no CyVerse profile")

    altered = False
    if profile['first_name'] != user.first_name:
        user.first_name = profile['first_name']
        altered = True
    if profile['last_name'] != user.last_name:
        user.last_name = profile['last_name']
        altered = True
    if profile['institution'] != user.profile.institution:
        user.profile.institution = profile['institution']
        altered = True

    # only write to DB if we change anything (avoids a network call if we don't need one)
    if altered:
        user.profile.save()
        user.save()

    return profile


def refresh_user_cyverse_tokens(user: User):
    access_token, refresh_token = terrain.refresh_tokens(username=user.username, refresh_token=user.profile.cyverse_refresh_token)
    user.profile.cyverse_access_token = access_token
    user.profile.cyverse_refresh_token = refresh_token
    user.profile.save()
    user.save()


async def get_user_github_profile(user: User) -> dict:
    profile = await sync_to_async(Profile.objects.get)(user=user)

    # if no GitHub auth token, the user hasn't linked their GitHub account yet
    if profile.github_token is None or profile.github_token == '':
        logger.warning(f"No GitHub token for user {user.username}")
        return dict()

    return await github.get_profile(profile.github_username, profile.github_token)


async def get_user_github_organizations(user: User) -> List[dict]:
    profile = await sync_to_async(Profile.objects.get)(user=user)

    # if no GitHub auth token, the user hasn't linked their GitHub account yet
    if profile.github_token is None or profile.github_token == '':
        logger.warning(f"No GitHub token for user {user.username}")
        return []

    return await github.list_user_organizations(profile.github_username, profile.github_token)


@sync_to_async
def filter_tasks(user: User, completed: bool = None):
    if completed is not None and completed:
        tasks = Task.objects.filter(user=user, completed__isnull=False)
    else:
        tasks = Task.objects.filter(user=user)
    return list(tasks)


@sync_to_async
def filter_agents(user: User = None, guest: User = None):
    if user is not None and guest is None:
        return list(Agent.objects.filter(user=user))
    elif user is None and guest is not None:
        return list(Agent.objects.filter(users_authorized__username=guest.username))
    else:
        raise ValueError(f"Expected either user or guest to be None")


def filter_online(users: List[User]) -> List[User]:
    """
    Selects only those users currently online by checking their Terrain token expiry times

    :param users: The list of users
    :return: The logged-in users
    """

    online = []
    for user in users:
        decoded_token = jwt.decode(user.profile.cyverse_access_token, options={
            'verify_signature': False,
            'verify_aud': False,
            'verify_iat': False,
            'verify_exp': False,
            'verify_iss': False
        })
        exp = datetime.fromtimestamp(decoded_token['exp'], timezone.utc)
        now = datetime.now(tz=timezone.utc)

        if now > exp:
            print(f"Session for {decoded_token['preferred_username']} expired at {exp.isoformat()}")
        else:
            print(f"Session for {decoded_token['preferred_username']} valid until {exp.isoformat()}")
            online.append(user)

    return online


@sync_to_async
def get_agent_user(agent: Agent):
    return agent.user


def notification_to_dict(notification: Notification) -> dict:
    return {
        'id': notification.guid,
        'username': notification.user.username,
        'created': notification.created.isoformat(),
        'message': notification.message,
        'read': notification.read,
    }


@sync_to_async
def get_task_user(task: Task):
    return task.user


@sync_to_async
def get_task_agent(task: Task):
    return task.agent


@sync_to_async
def get_task_project(task: Task):
    return task.project


@sync_to_async
def check_user_authentication(user):
    return user.is_authenticated


@sync_to_async
def get_profile_user(profile: Profile):
    return profile.user


@sync_to_async
def get_user_django_profile(user: User):
    profile = Profile.objects.get(user=user)
    return profile


def person_to_dict(user: User, role: str) -> dict:
    return {
        'name': f"{user.first_name} {user.last_name}",
        'email': user.email,
        'username': user.username,
        'affiliation': user.profile.institution,
        'role': role,
    }


# usage stats/demographics info


def count_institutions():
    return list(Profile.objects.exclude(institution__exact='').values('institution').annotate(Count('institution')))


def get_institutions(invalidate: bool = False) -> dict:
    redis = RedisClient.get()
    cached = list(redis.scan_iter(match=f"institutions/*"))
    institutions = dict()

    if invalidate:
        # count members per institution
        counts = {i['institution'].lower(): i['institution__count'] for i in count_institutions()}

        for k in counts.keys():
            # get institution information (TODO: can we send all the requests concurrently?)
            # TODO: need to make sure this doesn't exceed the free plan rate limit
            result = async_to_sync(mapbox.get_institution)(k, settings.MAPBOX_TOKEN)

            # reconstruct institution name with proper capitalization from Mapbox result
            # TODO: are there any edge cases this might fail for?
            name = ' '.join(result['query'])

            # if Mapbox returned no results, we can't return geocode information
            if len(result['features']) == 0:
                logger.warning(f"No results from Mapbox for institution: {name}")
                institutions[name] = {
                    'institution': name,
                    'count': counts[name] if name in counts else 0,
                    'geocode': None
                }
            # if we got results, pick the top one
            else:
                feature = result['features'][0]
                feature['id'] = name
                feature['properties'] = {
                    'name': name,
                    'count': counts[name]
                }
                institutions[name] = {
                    'institution': name,
                    'count': counts[name],
                    'geocode': feature
                }

        for name, institution in institutions.items(): redis.set(f"institutions/{name}", json.dumps(institution))
    else:
        for institution in cached:
            if institution is not None:
                institutions[institution.decode('utf-8')] = json.loads(redis.get(institution))

    return institutions


def get_total_counts(invalidate: bool = False) -> dict:
    redis = RedisClient.get()
    cached = redis.get("stats_counts")

    if cached is None or invalidate:
        users = User.objects.count()
        online = len(filter_online(User.objects.all()))  # TODO store this in the DB each time the user logs in
        wfs = [json.loads(redis.get(key)) for key in redis.scan_iter('workflows/*')]
        devs = list(set([wf['repo']['owner']['login'] for wf in wfs]))
        workflows = len(wfs)
        developers = len(devs)
        agents = Agent.objects.count()
        tasks = TaskCounter.load().count
        running = len(list(Task.objects.exclude(status__in=[TaskStatus.SUCCESS, TaskStatus.FAILURE, TaskStatus.TIMEOUT, TaskStatus.CANCELED])))
        counts = {
            'users': users,
            'online': online,
            'workflows': workflows,
            'developers': developers,
            'agents': agents,
            'tasks': tasks,
            'running': running
        }

        redis.set("stats_counts", json.dumps(counts))
    else:
        counts = json.loads(cached)

    return counts


def get_aggregate_timeseries(invalidate: bool = False) -> dict:
    redis = RedisClient.get()
    cached = redis.get("total_timeseries")

    if cached is None or invalidate:
        users_total = get_users_total_timeseries()
        tasks_total = get_tasks_total_timeseries()
        tasks_usage = get_tasks_usage_timeseries()
        workflows_usage = get_workflows_usage_timeseries()
        agents_usage = get_agents_usage_timeseries()
        series = {
            'users_total': users_total,
            'tasks_total': tasks_total,
            'tasks_usage': tasks_usage,
            'agents_usage': agents_usage,
            'workflows_usage': workflows_usage,
        }

        redis.set("total_timeseries", json.dumps(series))
    else:
        series = json.loads(cached)

    return series


def get_user_timeseries(user: User, invalidate: bool = False) -> dict:
    redis = RedisClient.get()
    cached = redis.get(f"user_timeseries/{user.username}")

    if cached is None or invalidate:
        tasks_usage = get_tasks_usage_timeseries(user=user)
        workflows_usage = get_workflows_usage_timeseries(user)
        agents_usage = get_agents_usage_timeseries(user)
        series = {
            'tasks_usage': tasks_usage,
            'agents_usage': agents_usage,
            'workflows_usage': workflows_usage
        }

        redis.set(f"user_timeseries/{user.username}", json.dumps(series))
    else:
        series = json.loads(cached)

    return series


def get_users_total_timeseries() -> List[Tuple[str, int]]:
    return [(user.profile.created.isoformat(), i + 1) for i, user in enumerate(User.objects.all().order_by('profile__created'))]


def get_tasks_total_timeseries() -> List[Tuple[str, int]]:
    return [(task['created'].isoformat(), i + 1) for i, task in enumerate(Task.objects.all().values('created').order_by('created'))]


# TODO: refactor like below
def get_tasks_usage_timeseries(interval_seconds: int = 600, user: User = None) -> dict:
    tasks = Task.objects.all() if user is None else Task.objects.filter(user=user).order_by('-completed')[:100]  # TODO make limit configurable
    series = dict()

    # return early if no tasks
    if len(tasks) == 0:
        return series

    # find the running interval for each task
    start_end_times = dict()
    for task in tasks:
        start_end_times[task.guid] = (task.created, task.completed if task.completed is not None else timezone.now())

    # count the number of running tasks for each value in the time domain
    start = min([v[0] for v in start_end_times.values()])
    end = max(v[1] for v in start_end_times.values())
    for t in range(int(start.timestamp()), int(end.timestamp()), interval_seconds):
        running = len([1 for k, se in start_end_times.items() if int(se[0].timestamp()) <= t <= int(se[1].timestamp())])
        series[t] = running

    # smooth timeseries with LOESS regression
    series_keys = list(series.keys())
    series_frame = pd.DataFrame({'X': series_keys, 'Y': list(series.values())})
    smoothed_frame = loess.regress(series_frame, bandwidth=int(interval_seconds / 5), num_pts=int(len(series_keys) / 2))
    series = {datetime.fromtimestamp(row['X']).isoformat(): row['Y'] for i, row in smoothed_frame.iterrows()}

    return series


def get_workflow_usage_timeseries(owner: str, name: str, branch: str, invalidate: bool = False) -> dict:
    redis = RedisClient.get()
    cached = redis.get(f"workflow_timeseries/{owner}/{name}/{branch}")

    if cached is None or invalidate:
        series = dict()
        tasks = Task.objects.filter(
            workflow__repo__owner=owner,
            workflow__repo__name=name,
            workflow__repo__branch=branch)

        # return early if no tasks
        if len(tasks) == 0:
            return series

        # count tasks per workflow
        for task in tasks:
            timestamp = datetime.combine(task.created.date(), datetime.min.time()).isoformat()
            if timestamp not in series: series[timestamp] = 0
            series[timestamp] = series[timestamp] + 1

        redis.set(f"workflow_timeseries/{owner}/{name}/{branch}", json.dumps(series))
    else:
        series = json.loads(cached)

    return series


def get_workflows_usage_timeseries(user: User = None) -> dict:
    # get stats moving window width from settings
    window_width_days = int(settings.STATS_WINDOW_WIDTH_DAYS)

    # starting date of window
    start = timezone.now().date() - timedelta(days=window_width_days)

    # if a user is provided, filter only tasks owned by that user, otherwise public tasks
    tasks = Task.objects.filter(workflow__public=True, created__gte=start) if user is None else Task.objects.filter(user=user,
                                                                                                                    created__gte=start)
    tasks = tasks.order_by('-created')  # chronological order by start time

    # to store timeseries (key is workflow owner/name/branch, value is series)
    series = dict()

    # return empty if no tasks
    if len(tasks) == 0: return series

    # loop over days from start date to now and count tasks occurring per workflow on each day
    dates = [start + timedelta(days=n) for n in range(window_width_days + 1)]
    for date in dates:
        # tasks created on this date
        tasks_today = tasks.filter(created__date=date)

        # count tasks per workflow
        for task in tasks_today:
            workflow = f"{task.workflow_owner}/{task.workflow_name}/{task.workflow_branch}"
            if workflow not in series: series[workflow] = dict()
            timestamp = datetime.combine(task.created.date(), datetime.min.time()).isoformat()
            if timestamp not in series[workflow]: series[workflow][timestamp] = 0
            series[workflow][timestamp] = series[workflow][timestamp] + 1

    # sort dictionary by keys (dates)
    for key in series.keys():
        series[key] = OrderedDict(sorted(series[key].items(), key=lambda x: x[0]))

    return series


# TODO: refactor like above
def get_agent_usage_timeseries(name) -> dict:
    agent = Agent.objects.get(name=name)
    tasks = Task.objects.filter(agent=agent).order_by('-created')
    series = dict()

    if len(tasks) == 0:
        return series

    # count tasks per agent
    for task in tasks:
        timestamp = datetime.combine(task.created.date(), datetime.min.time()).isoformat()
        if timestamp not in series: series[timestamp] = 0
        series[timestamp] = series[timestamp] + 1

    return series


# TODO: refactor like above
def get_agents_usage_timeseries(user: User = None) -> dict:
    tasks = Task.objects.filter(agent__public=True).order_by('-created') if user is None else Task.objects.filter(user=user).order_by('-created')[
                                                                                              :100]
    series = dict()

    # return early if no tasks
    if len(tasks) == 0:
        return series

    # count tasks per agent
    for task in tasks:
        agent = task.agent

        # if task predates our adding agent FK to model, might be None... just skip it
        if agent is None:
            continue

        if agent.name not in series: series[agent.name] = dict()
        timestamp = datetime.combine(task.created.date(), datetime.min.time()).isoformat()
        if timestamp not in series[agent.name]: series[agent.name][timestamp] = 0
        series[agent.name][timestamp] = series[agent.name][timestamp] + 1

    return series


async def calculate_user_statistics(user: User) -> dict:
    profile = await sync_to_async(Profile.objects.get)(user=user)
    all_tasks = await filter_tasks(user=user)
    completed_tasks = await filter_tasks(user=user, completed=True)
    total_tasks = len(all_tasks)
    total_time = sum([(task.completed - task.created).total_seconds() for task in completed_tasks])
    total_results = sum([len(task.results if task.results is not None else []) for task in completed_tasks])
    owned_workflows = [
        f"{workflow['repo']['owner']['login']}/{workflow['name'] if 'name' in workflow else '[unnamed]'}"
        for
        workflow in list_user_workflows(owner=profile.github_username)] if profile.github_username != '' else []
    used_workflows = [f"{task.workflow_owner}/{task.workflow_name}" for task in all_tasks]
    used_workflows_counter = Counter(used_workflows)
    unique_used_workflows = list(np.unique(used_workflows))
    owned_agents = [(await sync_to_async(agent_to_dict)(agent, user.username))['name'] for agent in
                    [agent for agent in await filter_agents(user=user) if agent is not None]]
    guest_agents = [(await sync_to_async(agent_to_dict)(agent, user.username))['name'] for agent in
                    [agent for agent in await filter_agents(user=user) if agent is not None]]
    used_agents = [(await sync_to_async(agent_to_dict)(agent, user.username))['name'] for agent in
                   [a for a in [await get_task_agent(task) for task in all_tasks] if a is not None]]
    used_projects = [(await sync_to_async(project_to_dict)(project)) for project in
                     [p for p in [await get_task_project(task) for task in all_tasks] if p is not None]]
    used_agents_counter = Counter(used_agents)
    used_projects_counter = Counter([f"{project['guid']} ({project['title']})" for project in used_projects])
    unique_used_agents = list(np.unique(used_agents))

    # owned_datasets = terrain.list_dir(f"/iplant/home/{user.username}", profile.cyverse_access_token)
    # guest_datasets = terrain.list_dir(f"/iplant/home/", profile.cyverse_access_token)
    tasks_running = await sync_to_async(get_tasks_usage_timeseries)(600, user)

    return {
        'total_tasks': total_tasks,
        'total_task_seconds': total_time,
        'total_task_results': total_results,
        'owned_workflows': owned_workflows,
        'workflow_usage': {
            'values': [used_workflows_counter[workflow] for workflow in unique_used_workflows],
            'labels': unique_used_workflows,
        },
        'agent_usage': {
            'values': [used_agents_counter[agent] for agent in unique_used_agents],
            'labels': unique_used_agents,
        },
        'project_usage': {
            'values': list(dict(used_projects_counter).values()),
            'labels': list(dict(used_projects_counter).keys()),
        },
        'task_status': {
            'values': [1 if task.status == 'success' else 0 for task in all_tasks],
            'labels': ['SUCCESS' if task.status == 'success' else 'FAILURE' for task in all_tasks],
        },
        'owned_agents': owned_agents,
        'guest_agents': guest_agents,
        'institution': profile.institution,
        'tasks_running': tasks_running
    }


def update_to_dict(update: NewsUpdate):
    return {
        'created': update.created.isoformat(),
        'content': update.content
    }
