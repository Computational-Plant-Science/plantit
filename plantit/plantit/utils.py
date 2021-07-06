import asyncio
import binascii
import fileinput
import json
import logging
import os
import pprint
import subprocess
import sys
import uuid
from pprint import pprint
from collections import Counter
from datetime import timedelta, datetime
from math import ceil
from os import environ
from os.path import isdir
from os.path import join
from pathlib import Path
from typing import List
from urllib.parse import quote_plus

import numpy as np
import requests
import yaml
from asgiref.sync import async_to_sync
from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from dateutil import parser
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Count
from django.utils import timezone

import plantit.github as github
import plantit.terrain as terrain
from plantit import settings
from plantit.agents.models import Agent, AgentAccessPolicy, AgentRole, AgentExecutor, AgentTask
from plantit.datasets.models import DatasetAccessPolicy
from plantit.docker import parse_image_components, image_exists
from plantit.misc import del_none, format_bind_mount, parse_bind_mount
from plantit.notifications.models import Notification
from plantit.redis import RedisClient
from plantit.ssh import SSH, execute_command
from plantit.tasks.models import DelayedTask, RepeatingTask, TaskStatus, JobQueueTask, TaskCounter
from plantit.tasks.models import Task
from plantit.tasks.options import BindMount
from plantit.tasks.options import PlantITCLIOptions, Parameter, Input, PasswordTaskAuth, KeyTaskAuth, InputKind
from plantit.users.models import Profile
from plantit.workflows.models import Workflow

logger = logging.getLogger(__name__)


# users

def list_users(github_token: str, invalidate: bool = False) -> List[dict]:
    redis = RedisClient.get()
    updated = redis.get(f"users_updated")

    # repopulate if empty or invalidation requested
    if updated is None or len(list(redis.scan_iter(match=f"users/*"))) == 0 or invalidate:
        repopulate_user_cache(github_token)
    else:
        age = (datetime.now() - datetime.fromtimestamp(float(updated)))
        age_secs = age.total_seconds()
        max_secs = (int(settings.USERS_REFRESH_MINUTES) * 60)

        # otherwise only if stale
        if age_secs > max_secs:
            logger.info(f"User cache is stale ({age_secs}s old, {age_secs - max_secs}s past limit), repopulating")
            repopulate_user_cache(github_token)

    return [json.loads(redis.get(key)) for key in redis.scan_iter(match=f"users/*")]


def repopulate_user_cache(github_token: str):
    redis = RedisClient.get()
    users = User.objects.all()
    mapped = []
    for user in list(users.exclude(profile__isnull=True)):
        if user.profile.github_username:
            github_profile = requests.get(f"https://api.github.com/users/{user.profile.github_username}",
                                          headers={'Authorization': f"Bearer {github_token}"}).json()
            if 'login' in github_profile:
                mapped.append({
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'github_username': user.profile.github_username,
                    'github_profile': github_profile
                })
            else:
                mapped.append({
                    'username': user.username,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                })
        else:
            mapped.append({
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
            })

    logger.info(f"Populating user cache")
    for user in mapped: redis.set(f"users/{user['username']}", json.dumps(user))


@sync_to_async
def get_profile_user(profile: Profile):
    return profile.user


@sync_to_async
def get_user_django_profile(user: User):
    return user.profile


def get_user_cyverse_profile(user: User) -> dict:
    profile = terrain.get_profile(user.username, user.profile.cyverse_access_token)
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
    profile = await get_user_django_profile(user)
    return await github.get_profile(profile.github_username, profile.github_token)


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


def get_user_statistics(user: User) -> dict:
    redis = RedisClient.get()
    stats_last_aggregated = user.profile.stats_last_aggregated

    if stats_last_aggregated is None:
        logger.info(f"No usage statistics for {user.username}. Aggregating stats...")
        stats = async_to_sync(calculate_user_statistics)(user)
        redis = RedisClient.get()
        redis.set(f"stats/{user.username}", json.dumps(stats))
        user.profile.stats_last_aggregated = timezone.now()
        user.profile.save()
    else:
        stats = redis.get(f"stats/{user.username}")
        stats_age_minutes = (timezone.now() - stats_last_aggregated).total_seconds() / 60

        if stats is None or stats_age_minutes > int(os.environ.get('USERS_STATS_REFRESH_MINUTES')):
            logger.info(f"{stats_age_minutes} elapsed since last aggregating usage statistics for {user.username}. Refreshing stats...")
            stats = async_to_sync(calculate_user_statistics)(user)
            redis = RedisClient.get()
            redis.set(f"stats/{user.username}", json.dumps(stats))
            user.profile.stats_last_aggregated = timezone.now()
            user.profile.save()
        else:
            stats = json.loads(stats)

    return stats


async def calculate_user_statistics(user: User) -> dict:
    all_tasks = await filter_tasks(user=user)
    completed_tasks = await filter_tasks(user=user, completed=True)
    profile = await get_user_django_profile(user)

    total_tasks = len(all_tasks)
    total_time = sum([(task.completed - task.created).total_seconds() for task in completed_tasks])
    total_results = sum([len(task.results if task.results is not None else []) for task in completed_tasks])
    owned_workflows = [f"{workflow['repo']['owner']['login']}/{workflow['config']['name'] if 'name' in workflow['config'] else '[unnamed]'}" for
                       workflow in await list_personal_workflows(owner=profile.github_username)] if profile.github_username != '' else []
    used_workflows = [f"{task.workflow_owner}/{task.workflow_name}" for task in all_tasks]
    used_workflows_counter = Counter(used_workflows)
    unique_used_workflows = list(np.unique(used_workflows))
    owned_agents = [(await sync_to_async(agent_to_dict)(agent, user))['name'] for agent in await filter_agents(user=user)]
    guest_agents = [(await sync_to_async(agent_to_dict)(agent, user))['name'] for agent in await filter_agents(guest=user)]
    used_agents = [(await sync_to_async(agent_to_dict)(await get_task_agent(task), user))['name'] for task in all_tasks]
    used_agents_counter = Counter(used_agents)
    unique_used_agents = list(np.unique(used_agents))
    # owned_datasets = terrain.list_dir(f"/iplant/home/{user.username}", profile.cyverse_access_token)
    # guest_datasets = terrain.list_dir(f"/iplant/home/", profile.cyverse_access_token)

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
        'task_status': {
            'values': [1 if task.status == 'success' else 0 for task in all_tasks],
            'labels': ['SUCCESS' if task.status == 'success' else 'FAILURE' for task in all_tasks],
        },
        'owned_agents': owned_agents,
        'guest_agents': guest_agents,
        'institution': profile.institution
    }


def get_or_create_user_keypair(username: str, overwrite: bool = False) -> str:
    """
    Creates an RSA-protected SSH keypair for the user and returns the public key (or gets the public key if a keypair already exists).
    To overwrite a pre-existing keypair, use the `invalidate` argument.

    Args:
        username: The user (CyVerse/Django username) to create a keypair for.
        overwrite: Whether to overwrite an existing keypair.

    Returns: The path to the newly created public key.
    """
    public_key_path = get_user_public_key_path(username)
    private_key_path = get_user_private_key_path(username)

    if public_key_path.is_file():
        if overwrite:
            logger.info(f"Keypair for {username} already exists, overwriting")
            public_key_path.unlink()
            private_key_path.unlink(missing_ok=True)
        else:
            logger.info(f"Keypair for {username} already exists")
    else:
        subprocess.run(f"ssh-keygen -b 2048 -t rsa -f {private_key_path} -N \"\"", shell=True)
        logger.info(f"Created keypair for {username}")

    with open(public_key_path, 'r') as key:
        return key.readlines()[0]


def get_user_private_key_path(username: str) -> Path:
    path = Path(f"{Path(settings.AGENT_KEYS).absolute()}/{username}")
    path.mkdir(exist_ok=True, parents=True)
    return Path(join(path, f"{username}_id_rsa"))


def get_user_public_key_path(username: str) -> Path:
    path = Path(f"{Path(settings.AGENT_KEYS).absolute()}/{username}")
    path.mkdir(exist_ok=True, parents=True)
    return Path(join(path, f"{username}_id_rsa.pub"))


def repopulate_institutions_cache():
    redis = RedisClient.get()
    institution_counts = list(Profile.objects.exclude(institution__exact='').values('institution').annotate(Count('institution')))

    for institution_count in institution_counts:
        institution = institution_count['institution']
        count = institution_count['institution__count']

        place = quote_plus(institution)
        response = requests.get(f"https://api.mapbox.com/geocoding/v5/mapbox.places/{place}.json?access_token={settings.MAPBOX_TOKEN}")
        content = response.json()
        feature = content['features'][0]
        feature['id'] = institution
        feature['properties'] = {
            'name': institution,
            'count': count
        }
        redis.set(f"institutions/{institution}", json.dumps({
            'institution': institution,
            'count': count,
            'geocode': feature
        }))

    redis.set("institutions_updated", timezone.now().timestamp())


def list_institutions(invalidate: bool = False) -> List[dict]:
    redis = RedisClient.get()
    updated = redis.get('institutions_updated')

    # repopulate if empty or invalidation requested
    if updated is None or len(list(redis.scan_iter(match=f"institutions/*"))) == 0 or invalidate:
        logger.info(f"Populating user institution cache")
        repopulate_institutions_cache()
    else:
        age = (datetime.now() - datetime.fromtimestamp(float(updated)))
        age_secs = age.total_seconds()
        max_secs = (int(settings.MAPBOX_FEATURE_REFRESH_MINUTES) * 60)

        # otherwise only if stale
        if age_secs > max_secs:
            logger.info(f"User institution cache is stale ({age_secs}s old, {age_secs - max_secs}s past limit), repopulating")
            repopulate_institutions_cache()

    return [json.loads(redis.get(key)) for key in redis.scan_iter(match='institutions/*')]


# workflows

@sync_to_async
def list_workflows(user: User = None, public: bool = None):
    workflows = Workflow.objects.all()
    if user is not None: workflows = workflows.filter(user=user)
    if public is not None: workflows = workflows.filter(public=public)
    return list(workflows)


@sync_to_async
def get_workflow_user(workflow: Workflow):
    return workflow.user


async def workflow_to_dict(workflow: Workflow, token: str) -> dict:
    bundle = await github.get_repo_bundle(
        workflow.repo_owner,
        workflow.repo_name,
        token)
    return {
        'config': bundle['config'],
        'repo': bundle['repo'],
        'validation': bundle['validation'],
        'public': workflow.public,
        'bound': True
    }


async def repopulate_personal_workflow_cache(owner: str):
    if owner is None or owner == '': raise ValueError(f"No owner name provided")

    try:
        profile = await sync_to_async(Profile.objects.get)(github_username=owner)
        user = await get_profile_user(profile)
    except MultipleObjectsReturned:
        logger.warning(f"Multiple users bound to Github user {owner}!")
        return
    except:
        logger.warning(f"Github user {owner} does not exist")
        return

    empty_personal_workflow_cache(owner)

    profile = await get_user_django_profile(user)
    owned = await list_workflows(user=user)
    bind = asyncio.gather(*[workflow_to_dict(workflow, profile.github_token) for workflow in owned])
    tasks = await asyncio.gather(*[bind, github.list_connectable_repos_by_owner(owner, profile.github_token)])
    bound = tasks[0]
    bindable = tasks[1]
    both = []

    for ba in bindable:
        if not any(['name' in ed['config'] and 'name' in ba['config'] and ed['config']['name'] == ba['config']['name'] for ed in bound]):
            ba['public'] = False
            ba['bound'] = False
            both.append(ba)

    missing = 0
    for bo in [b for b in bound if b['repo']['owner']['login'] == owner]:  # omit manually added workflows (e.g., owned by a GitHub Organization)
        name = bo['config']['name']
        if not any(['name' in ba['config'] and ba['config']['name'] == name for ba in bindable]):
            missing += 1
            logger.warning(f"Configuration file missing for {owner}'s workflow {name}")
            bo['validation'] = {
                'is_valid': False,
                'errors': ["Configuration file missing"]
            }
        both.append(bo)

    redis = RedisClient.get()
    for workflow in both: redis.set(f"workflows/{owner}/{workflow['repo']['name']}", json.dumps(del_none(workflow)))
    redis.set(f"workflows_updated/{owner}", timezone.now().timestamp())
    logger.info(f"Added {len(bound)} bound, {len(bindable) - len(bound)} bindable, {len(both)} total to {owner}'s workflow cache" + (
        "" if missing == 0 else f"({missing} with missing configuration files)"))


async def repopulate_public_workflow_cache(token: str):
    redis = RedisClient.get()
    public_workflows = await list_workflows(public=True)
    encountered_users = []

    for workflow, user in list(zip(public_workflows, [await get_workflow_user(workflow) for workflow in public_workflows])):
        if user is None:
            # workflow is not owned by any particular user (e.g., added by admins for shared GitHub group) so explicitly refresh the binding
            logger.info(f"Binding unclaimed workflow {workflow.repo_owner}/{workflow.repo_name}")
            bundle = await workflow_to_dict(workflow, token)
            redis.set(f"workflows/{workflow.repo_owner}/{workflow.repo_name}", json.dumps(del_none(bundle)))
        else:
            # otherwise refresh all the workflow owner's workflows (but only once)
            if user.username in encountered_users: continue
            profile = await get_user_django_profile(user)
            empty_personal_workflow_cache(profile.github_username)
            await repopulate_personal_workflow_cache(profile.github_username)
            encountered_users.append(user.username)

    redis.set(f"public_workflows_updated", timezone.now().timestamp())


async def list_public_workflows(token: str, invalidate: bool = False) -> List[dict]:
    redis = RedisClient.get()
    updated = redis.get('public_workflows_updated')

    # repopulate if empty or invalidation requested
    if updated is None or len(list(redis.scan_iter(match=f"workflows/*"))) == 0 or invalidate:
        logger.info(f"Populating public workflow cache")
        await repopulate_public_workflow_cache(token)
    else:
        age = (datetime.now() - datetime.fromtimestamp(float(updated)))
        age_secs = age.total_seconds()
        max_secs = (int(settings.WORKFLOWS_REFRESH_MINUTES) * 60)

        # otherwise only if stale
        if age_secs > max_secs:
            logger.info(f"Public workflow cache is stale ({age_secs}s old, {age_secs - max_secs}s past limit), repopulating")
            await repopulate_public_workflow_cache(token)

    workflows = [json.loads(redis.get(key)) for key in redis.scan_iter(match='workflows/*')]
    return [workflow for workflow in workflows if workflow['public']]


async def list_personal_workflows(owner: str, invalidate: bool = False) -> List[dict]:
    redis = RedisClient.get()
    updated = redis.get(f"workflows_updated/{owner}")

    # repopulate if empty or invalidation requested
    if updated is None or len(list(redis.scan_iter(match=f"workflows/{owner}/*"))) == 0 or invalidate:
        await repopulate_personal_workflow_cache(owner)
    else:
        age = (datetime.now() - datetime.fromtimestamp(float(updated)))
        age_secs = age.total_seconds()
        max_secs = (int(settings.WORKFLOWS_REFRESH_MINUTES) * 60)

        # otherwise only if stale
        if age_secs > max_secs:
            logger.info(f"GitHub user {owner}'s workflow cache is stale ({age_secs}s old, {age_secs - max_secs}s past limit), repopulating")
            await repopulate_personal_workflow_cache(owner)

    return [json.loads(redis.get(key)) for key in redis.scan_iter(match=f"workflows/{owner}/*")]


async def get_workflow(owner: str, name: str, token: str, invalidate: bool = False) -> dict:
    redis = RedisClient.get()
    updated = redis.get(f"workflows_updated/{owner}")
    workflow = redis.get(f"workflows/{owner}/{name}")

    if updated is None or workflow is None or invalidate:
        try:
            workflow = await sync_to_async(Workflow.objects.get)(repo_owner=owner, repo_name=name)
        except:
            raise ValueError(f"Workflow {owner}/{name} not found")

        workflow = await workflow_to_dict(workflow, token)
        redis.set(f"workflows/{owner}/{name}", json.dumps(del_none(workflow)))

    return workflow


def empty_personal_workflow_cache(owner: str):
    redis = RedisClient.get()
    keys = list(redis.scan_iter(match=f"workflows/{owner}/*"))
    cleaned = len(keys)
    for key in keys: redis.delete(key)
    logger.info(f"Emptied {cleaned} workflows from GitHub user {owner}'s cache")
    return cleaned


# tasks

@sync_to_async
def get_task_user(task: Task):
    return task.user


@sync_to_async
def get_task_agent(task: Task):
    return task.agent


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
        raise Exception(f"Failed to parse job ID from: '{line}'")


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


def parse_task_cli_options(task: Task) -> (List[str], PlantITCLIOptions):
    # update config before uploading
    config = task.workflow['config']
    config['workdir'] = join(task.agent.workdir, task.guid)
    config['log_file'] = f"{task.guid}.{task.agent.name.lower()}.log"
    if 'output' in config and 'from' in config['output']:
        if config['output']['from'] is not None and config['output']['from'] != '':
            config['output']['from'] = join(task.agent.workdir, task.workdir, config['output']['from'])

    # if we have outputs, make sure we don't push configuration or job scripts
    if 'output' in config:
        config['output']['exclude']['names'] = [
            f"{task.guid}.yaml",
            "template_local_run.sh",
            "template_slurm_run.sh"]

    # jobqueue = None if 'jobqueue' not in config['agent'] else config['agent']['jobqueue']
    # new_flow = map_workflow_config_to_cli_config(config, task, jobqueue)
    # launcher = task.agent.launcher  # whether to use TACC launcher
    # if task.agent.launcher: del new_flow['jobqueue']

    errors = []
    image = None
    if not isinstance(config['image'], str):
        errors.append('Attribute \'image\' must not be a str')
    elif config['image'] == '':
        errors.append('Attribute \'image\' must not be empty')
    else:
        image = config['image']
        if 'docker' in image:
            image_owner, image_name, image_tag = parse_image_components(image)
            if not image_exists(image_name, image_owner, image_tag):
                errors.append(f"Image '{image}' not found on Docker Hub")

    work_dir = None
    if not isinstance(config['workdir'], str):
        errors.append('Attribute \'workdir\' must not be a str')
    elif config['workdir'] == '':
        errors.append('Attribute \'workdir\' must not be empty')
    else:
        work_dir = config['workdir']

    command = None
    if not isinstance(config['commands'], str):
        errors.append('Attribute \'commands\' must not be a str')
    elif config['commands'] == '':
        errors.append('Attribute \'commands\' must not be empty')
    else:
        command = config['commands']

    parameters = None
    if 'parameters' in config:
        if not all(['name' in param and
                    param['name'] is not None and
                    param['name'] != '' and
                    'value' in param and
                    param['value'] is not None and
                    param['value'] != ''
                    for param in config['parameters']]):
            errors.append('Every parameter must have a non-empty \'name\' and \'value\'')
        else:
            parameters = [Parameter(key=param['name'], value=param['value']) for param in config['parameters']]

    bind_mounts = None
    if 'bind_mounts' in config:
        if not all(mount_point != '' for mount_point in config['bind_mounts']):
            errors.append('Every mount point must be non-empty')
        else:
            bind_mounts = [parse_bind_mount(work_dir, mount_point) for mount_point in config['bind_mounts']]

    input = None
    if 'input' in config:
        if 'kind' not in config['input']:
            errors.append("Section \'input\' must include attribute \'kind\'")
        if 'path' not in config['input']:
            errors.append("Section \'input\' must include attribute \'path\'")

        kind = config['input']['kind']
        path = config['input']['path']
        if kind == 'file':
            input = Input(path=path, kind='file')
        elif kind == 'files':
            input = Input(path=path, kind='files', patterns=config['input']['patterns'] if 'patterns' in config['input'] else None)
        elif kind == 'directory':
            input = Input(path=path, kind='directory')
        else:
            errors.append('Section \'input.kind\' must be \'file\', \'files\', or \'directory\'')

    log_file = None
    if 'log_file' in config:
        log_file = config['log_file']
        if not isinstance(log_file, str):
            errors.append('Attribute \'log_file\' must be a str')
        elif log_file.rpartition('/')[0] != '' and not isdir(log_file.rpartition('/')[0]):
            errors.append('Attribute \'log_file\' must be a valid file path')

    no_cache = None
    if 'no_cache' in config:
        no_cache = config['no_cache']
        if not isinstance(no_cache, bool):
            errors.append('Attribute \'no_cache\' must be a bool')

    gpu = None
    if 'gpu' in config:
        gpu = config['gpu']
        if not isinstance(gpu, bool):
            errors.append('Attribute \'gpu\' must be a bool')

    jobqueue = None
    if 'jobqueue' in config:
        jobqueue = config['jobqueue']
        # if not (
        #         'slurm' in jobqueue or 'yarn' in jobqueue or 'pbs' in jobqueue or 'moab' in jobqueue or 'sge' in jobqueue or 'lsf' in jobqueue or 'oar' in jobqueue or 'kube' in jobqueue):
        #     raise ValueError(f"Unsupported jobqueue configuration: {jobqueue}")

        if 'queue' in jobqueue:
            if not isinstance(jobqueue['queue'], str):
                errors.append('Section \'jobqueue\'.\'queue\' must be a str')
        if 'project' in jobqueue:
            if not isinstance(jobqueue['project'], str):
                errors.append('Section \'jobqueue\'.\'project\' must be a str')
        if 'walltime' in jobqueue:
            if not isinstance(jobqueue['walltime'], str):
                errors.append('Section \'jobqueue\'.\'walltime\' must be a str')
        if 'cores' in jobqueue:
            if not isinstance(jobqueue['cores'], int):
                errors.append('Section \'jobqueue\'.\'cores\' must be a int')
        if 'processes' in jobqueue:
            if not isinstance(jobqueue['processes'], int):
                errors.append('Section \'jobqueue\'.\'processes\' must be a int')
        if 'extra' in jobqueue and not all(extra is str for extra in jobqueue['extra']):
            errors.append('Section \'jobqueue\'.\'extra\' must be a list of str')
        if 'header_skip' in jobqueue and not all(extra is str for extra in jobqueue['header_skip']):
            errors.append('Section \'jobqueue\'.\'header_skip\' must be a list of str')

    options = PlantITCLIOptions(
        workdir=work_dir,
        image=image,
        command=command)

    if input is not None: options['input'] = input
    if parameters is not None: options['parameters'] = parameters
    if bind_mounts is not None: options['bind_mounts'] = bind_mounts
    # if checksums is not None: options['checksums'] = checksums
    if log_file is not None: options['log_file'] = log_file
    if jobqueue is not None: options['jobqueue'] = jobqueue
    if no_cache is not None: options['no_cache'] = no_cache
    if gpu is not None: options['gpu'] = gpu

    return errors, options


def create_task(username: str, agent_name: str, workflow: dict, name: str = None, guid: str = None) -> Task:
    repo_owner = workflow['repo']['owner']['login']
    repo_name = workflow['repo']['name']
    agent = Agent.objects.get(name=agent_name)
    user = User.objects.get(username=username)
    if guid is None: guid = str(uuid.uuid4())  # if the browser client hasn't set a GUID, create one
    now = timezone.now()

    task = JobQueueTask.objects.create(
        guid=guid,
        name=name,
        user=user,
        workflow=workflow,
        workflow_owner=repo_owner,
        workflow_name=repo_name,
        agent=agent,
        status=TaskStatus.CREATED,
        created=now,
        updated=now,
        token=binascii.hexlify(
            os.urandom(
                20)).decode()) \
        if agent.executor != AgentExecutor.LOCAL else \
        Task.objects.create(
            guid=guid,
            name=guid if name is None else name,
            user=user,
            workflow=workflow,
            workflow_owner=repo_owner,
            workflow_name=repo_name,
            agent=agent,
            status=TaskStatus.CREATED,
            created=now,
            updated=now,
            token=binascii.hexlify(os.urandom(20)).decode())

    # add repo logo
    if 'logo' in workflow['config']:
        logo_path = workflow['config']['logo']
        task.workflow_image_url = f"https://raw.githubusercontent.com/{repo_name}/{repo_owner}/master/{logo_path}"

    for tag in workflow['config']['tags']: task.tags.add(tag)  # add task tags
    task.workdir = f"{task.guid}/"  # use GUID for working directory name
    task.save()

    counter = TaskCounter.load()
    counter.count = counter.count + 1
    counter.save()

    return task


def configure_task_environment(task: Task, ssh: SSH):
    log_task_status(task, [f"Verifying configuration"])
    async_to_sync(push_task_event)(task)

    parse_errors, cli_options = parse_task_cli_options(task)
    if len(parse_errors) > 0: raise ValueError(f"Failed to parse task options: {' '.join(parse_errors)}")

    work_dir = join(task.agent.workdir, task.guid)
    log_task_status(task, [f"Creating working directory"])
    async_to_sync(push_task_event)(task)

    list(execute_command(ssh=ssh, precommand=':', command=f"mkdir {work_dir}"))

    log_task_status(task, [f"Uploading task executable"])
    async_to_sync(push_task_event)(task)

    upload_task_executables(task, ssh, cli_options)

    log_task_status(task, [f"Uploading task definition"])
    async_to_sync(push_task_event)(task)

    with ssh.client.open_sftp() as sftp:
        # TODO remove this utter hack
        if 'input' in cli_options:
            kind = cli_options['input']['kind']
            path = cli_options['input']['path']
            if kind == InputKind.DIRECTORY or kind == InputKind.FILES:
                cli_options['input']['path'] = 'input'
            else:
                cli_options['input']['path'] = f"input/{path.rpartition('/')[2]}"

        if task.agent.executor == AgentExecutor.LOCAL: del cli_options['jobqueue']

        sftp.chdir(work_dir)
        with sftp.open(f"{task.guid}.yaml", 'w') as cli_file:
            yaml.dump(del_none(cli_options), cli_file, default_flow_style=False)
        if 'input' in cli_options: sftp.mkdir(join(work_dir, 'input'))


def compose_task_singularity_command(
        work_dir: str,
        image: str,
        command: str,
        bind_mounts: List[BindMount] = None,
        parameters: List[Parameter] = None,
        no_cache: bool = False,
        gpu: bool = False,
        docker_username: str = None,
        docker_password: str = None) -> str:
    cmd = f"singularity exec --home {work_dir}"

    if bind_mounts is not None:
        if len(bind_mounts) > 0:
            cmd += (' --bind ' + ','.join([format_bind_mount(work_dir, mount_point) for mount_point in bind_mounts]))
        else:
            raise ValueError(f"List expected for `bind_mounts`")

    if parameters is None:
        parameters = []
    parameters.append(Parameter(key='WORKDIR', value=work_dir))
    for parameter in parameters:
        print(f"Replacing '{parameter['key'].upper()}' with '{parameter['value']}'")
        command = command.replace(f"${parameter['key'].upper()}", str(parameter['value']))

    if no_cache:
        cmd += ' --disable-cache'

    if gpu:
        cmd += ' --nv'

    cmd += f" {image} {command}"
    print(f"Using command: '{cmd}'")

    # we don't necessarily want to reveal Docker auth info to the end user, so print the command before adding Docker env variables
    if docker_username is not None and docker_password is not None:
        cmd = f"SINGULARITY_DOCKER_USERNAME={docker_username} SINGULARITY_DOCKER_PASSWORD={docker_password} " + cmd

    return cmd


def compose_task_pull_command(task: Task, options: PlantITCLIOptions) -> str:
    if 'input' not in options: return ''
    input = options['input']
    if input is None: return ''
    kind = input['kind']

    if input['kind'] != InputKind.FILE and 'patterns' in input:
        # allow for both spellings of JPG
        patterns = [pattern.lower() for pattern in input['patterns']]
        if 'jpg' in patterns and 'jpeg' not in patterns:
            patterns.append("jpeg")
        elif 'jpeg' in patterns and 'jpg' not in patterns:
            patterns.append("jpg")
    else:
        patterns = []

    command = f"plantit terrain pull \"{input['path']}\"" \
              f" -p \"{join(task.agent.workdir, task.workdir, 'input')}\"" \
              f" {' '.join(['--pattern ' + pattern for pattern in patterns])}" \
              f""f" --terrain_token {task.user.profile.cyverse_access_token}"

    if task.agent.callbacks:
        callback_url = settings.API_URL + 'tasks/' + task.guid + '/status/'
        command += f""f" --plantit_url '{callback_url}' --plantit_token '{task.token}'"

    logger.info(f"Using pull command: {command}")
    return command


def compose_task_run_commands(task: Task, options: PlantITCLIOptions, inputs: List[str]) -> List[str]:
    docker_username = environ.get('DOCKER_USERNAME', None)
    docker_password = environ.get('DOCKER_PASSWORD', None)
    commands = []

    # if this resource uses TACC's launcher, create a parameter sweep script to invoke the Singularity container
    if task.agent.launcher:
        commands.append(f"export LAUNCHER_WORKDIR={join(task.agent.workdir, task.workdir)}\n")
        commands.append(f"export LAUNCHER_JOB_FILE={os.environ.get('LAUNCHER_SCRIPT_NAME')}\n")
        commands.append("$LAUNCHER_DIR/paramrun\n")
    # otherwise use the CLI
    else:
        command = f"plantit run {task.guid}.yaml"
        if task.agent.job_array and len(inputs) > 0:
            command += f" --slurm_job_array"

        if docker_username is not None and docker_password is not None:
            command += f" --docker_username {docker_username} --docker_password {docker_password}"

        if task.agent.callbacks:
            callback_url = settings.API_URL + 'tasks/' + task.guid + '/status/'
            command += f""f" --plantit_url '{callback_url}' --plantit_token '{task.token}'"

        commands.append(command)

    newline = '\n'
    logger.info(f"Using CLI commands: {newline.join(commands)}")
    return commands


def compose_task_zip_command(task: Task, options: PlantITCLIOptions) -> str:
    # if 'output' not in options: return ''
    output = options['output'] if 'output' in options else dict()
    # if output is None: return ''

    command = f"plantit zip {output['from'] if 'from' in output != '' else '.'} -o . -n {task.guid}"
    logs = [f"{task.guid}.{task.agent.name.lower()}.log"]
    command = f"{command} {' '.join(['--include_pattern ' + pattern for pattern in logs])}"

    if 'include' in output:
        if 'patterns' in output['include']:
            command = f"{command} {' '.join(['--include_pattern ' + pattern for pattern in output['include']['patterns']])}"
        if 'names' in output['include']:
            command = f"{command} {' '.join(['--include_name ' + pattern for pattern in output['include']['names']])}"
        if 'patterns' in output['exclude']:
            command = f"{command} {' '.join(['--exclude_pattern ' + pattern for pattern in output['exclude']['patterns']])}"
        if 'names' in output['exclude']:
            command = f"{command} {' '.join(['--exclude_name ' + pattern for pattern in output['exclude']['names']])}"

    logger.info(f"Using zip command: {command}")
    return command


def compose_task_push_command(task: Task, options: PlantITCLIOptions) -> str:
    # TODO

    # add push command if we have a destination
    # if 'to' in output and output['to'] is not None:
    #     push_commands = f"plantit terrain push {output['to']}" \
    #                     f" -p {join(run.work_dir, output['from'])}" \
    #                     f" --plantit_url '{callback_url}'"

    #     if 'include' in output:
    #         if 'patterns' in output['include']:
    #             push_commands = push_commands + ' '.join(
    #                 ['--include_pattern ' + pattern for pattern in output['include']['patterns']])
    #         if 'names' in output['include']:
    #             push_commands = push_commands + ' '.join(['--include_name ' + pattern for pattern in output['include']['names']])
    #         if 'patterns' in output['exclude']:
    #             push_commands = push_commands + ' '.join(
    #                 ['--exclude_pattern ' + pattern for pattern in output['exclude']['patterns']])
    #         if 'names' in output['exclude']:
    #             push_commands = push_commands + ' '.join(['--exclude_name ' + pattern for pattern in output['exclude']['names']])

    #     if run.resource.callbacks:
    #         push_commands += f""f" --plantit_url '{callback_url}' --plantit_token '{run.token}'"

    #     push_commands += '\n'
    #     script.write(push_commands)
    #     logger.info(f"Using push command: {push_commands}")

    return ''


def compose_task_run_script(task: Task, options: PlantITCLIOptions, template: str) -> List[str]:
    with open(template, 'r') as template_file:
        template_header = [line for line in template_file]

    if 'input' in options and options['input'] is not None:
        kind = options['input']['kind']
        path = options['input']['path']
        cyverse_token = task.user.profile.cyverse_access_token
        inputs = [terrain.get_file(path, cyverse_token)] if kind == InputKind.FILE else terrain.list_dir(path, cyverse_token)
    else:
        inputs = []

    resource_requests = [] if task.agent.executor == AgentExecutor.LOCAL else compose_jobqueue_task_resource_requests(task, options, inputs)
    pull_command = compose_task_pull_command(task, options)
    run_commands = compose_task_run_commands(task, options, inputs)
    zip_command = compose_task_zip_command(task, options)
    push_command = compose_task_push_command(task, options)

    return template_header + resource_requests + [task.agent.pre_commands] + [pull_command] + run_commands + [zip_command] + [push_command]


def compose_jobqueue_task_resource_requests(task: Task, options: PlantITCLIOptions, inputs: List[str]) -> List[str]:
    nodes = min(len(inputs), task.agent.max_nodes) if inputs is not None and not task.agent.job_array else 1

    if 'jobqueue' not in 'options': return []
    gpu = task.agent.gpu and ('gpu' in options and options['gpu'])
    jobqueue = options['jobqueue']
    commands = []

    if 'cores' in jobqueue: commands.append(f"#SBATCH --cpus-per-task={int(jobqueue['cores'])}\n")
    if 'memory' in jobqueue and not has_virtual_memory(task.agent): commands.append(f"#SBATCH --mem={jobqueue['memory']}\n")
    if 'walltime' in task.workflow['config']:
        split_time = task.workflow['config']['walltime'].split(':')
        hours = int(split_time[0])
        minutes = int(split_time[1])
        seconds = int(split_time[2])
        walltime = timedelta(hours=hours, minutes=minutes, seconds=seconds)

        # adjust walltime to compensate for inputs processed in parallel [requested walltime * input files / nodes]
        adjusted = walltime * (len(inputs) / nodes) if len(inputs) > 0 else walltime

        # round up to the nearest hour
        hours = f"{min(ceil(adjusted.total_seconds() / 60 / 60), task.agent.max_nodes)}"
        if len(hours) == 1: hours = f"0{hours}"
        adjusted_str = f"{hours}:00:00"

        log_task_status(task, [f"Using adjusted walltime {adjusted_str}"])
        async_to_sync(push_task_event)(task)

        task.job_requested_walltime = adjusted_str
        task.save()
        commands.append(f"#SBATCH --time={adjusted_str}\n")
    if gpu: commands.append(f"#SBATCH --gres=gpu:1\n")
    if task.agent.queue is not None and task.agent.queue != '': commands.append(
        f"#SBATCH --partition={task.agent.gpu_queue if gpu else task.agent.queue}\n")
    if task.agent.project is not None and task.agent.project != '': commands.append(f"#SBATCH -A {task.agent.project}\n")
    if len(inputs) > 0:
        if task.agent.job_array:
            commands.append(f"#SBATCH --array=1-{len(inputs)}\n")
        commands.append(f"#SBATCH -N {nodes}\n")
        commands.append(f"#SBATCH --ntasks={nodes}\n")
    else:
        commands.append(f"#SBATCH -N 1\n")
        commands.append("#SBATCH --ntasks=1\n")
    commands.append("#SBATCH --mail-type=END,FAIL\n")
    commands.append(f"#SBATCH --mail-user={task.user.email}\n")
    commands.append("#SBATCH --output=plantit.%j.out\n")
    commands.append("#SBATCH --error=plantit.%j.err\n")

    newline = '\n'
    logger.info(f"Using resource requests: {newline.join(commands)}")
    return commands


def compose_jobqueue_task_launcher_script(task: Task, options: PlantITCLIOptions) -> List[str]:
    docker_username = environ.get('DOCKER_USERNAME', None)
    docker_password = environ.get('DOCKER_PASSWORD', None)
    lines = []

    if 'input' in options:
        if options['input']['kind'] == 'files':
            files = list_task_input_files(task, options) if ('input' in options and options['input']['kind'] == 'files') else []
            for file in files:
                file_name = file.rpartition('/')[2]
                command = compose_task_singularity_command(
                    work_dir=options['workdir'],
                    image=options['image'],
                    command=options['command'],
                    parameters=(options['parameters'] if 'parameters' in options else []) + [
                        Parameter(key='INPUT', value=join(options['workdir'], 'input', file_name))],
                    bind_mounts=options['bind_mounts'],
                    no_cache=options['no_cache'],
                    gpu=options['gpu'],
                    docker_username=docker_username,
                    docker_password=docker_password)
                lines.append(command)
        elif options['input']['kind'] == 'directory':
            command = compose_task_singularity_command(
                work_dir=options['workdir'],
                image=options['image'],
                command=options['command'],
                parameters=(options['parameters'] if 'parameters' in options else []) + [
                    Parameter(key='INPUT', value=join(options['workdir'], 'input'))],
                bind_mounts=options['bind_mounts'],
                no_cache=options['no_cache'],
                gpu=options['gpu'],
                docker_username=docker_username,
                docker_password=docker_password)
            lines.append(command)
        elif options['input']['kind'] == 'file':
            file_name = options['input']['path'].rpartition('/')[2]
            command = compose_task_singularity_command(
                work_dir=options['workdir'],
                image=options['image'],
                command=options['command'],
                parameters=(options['parameters'] if 'parameters' in options else []) + [
                    Parameter(key='INPUT', value=join(options['workdir'], file_name))],
                bind_mounts=options['bind_mounts'],
                no_cache=options['no_cache'],
                gpu=options['gpu'],
                docker_username=docker_username,
                docker_password=docker_password)
            lines.append(command)
    else:
        command = compose_task_singularity_command(
            work_dir=options['workdir'],
            image=options['image'],
            command=options['command'],
            parameters=(options['parameters'] if 'parameters' in options else []),
            bind_mounts=options['bind_mounts'] if 'bind_mounts' in options else None,
            no_cache=options['no_cache'] if 'no_cache' in options else False,
            gpu=options['gpu'] if 'gpu' in options else False,
            docker_username=docker_username,
            docker_password=docker_password)
        lines.append(command)

    return lines


def upload_task_executables(task: Task, ssh: SSH, options: PlantITCLIOptions):
    with ssh.client.open_sftp() as sftp:
        workdir = join(task.agent.workdir, task.workdir)
        sftp.chdir(workdir)
        template_path = environ.get('CELERY_TEMPLATE_LOCAL_RUN_SCRIPT') if task.agent.executor == AgentExecutor.LOCAL else environ.get(
            'CELERY_TEMPLATE_SLURM_RUN_SCRIPT')
        with sftp.open(f"{task.guid}.sh", 'w') as task_script:
            task_commands = compose_task_run_script(task, options, template_path)
            for line in task_commands:
                if line != '': task_script.write(line + "\n")

        # if the selected agent uses the Launcher, create a parameter sweep script too
        if task.agent.launcher:
            with sftp.open(os.environ.get('LAUNCHER_SCRIPT_NAME'), 'w') as launcher_script:
                launcher_commands = compose_jobqueue_task_launcher_script(task, options)
                for line in launcher_commands:
                    if line != '': launcher_script.write(line + "\n")


def execute_local_task(task: Task, ssh: SSH):
    precommand = '; '.join(str(task.agent.pre_commands).splitlines()) if task.agent.pre_commands else ':'
    command = f"chmod +x {task.guid}.sh && ./{task.guid}.sh"
    workdir = join(task.agent.workdir, task.workdir)

    count = 0
    lines = []
    for line in execute_command(ssh=ssh, precommand=precommand, command=command, directory=workdir, allow_stderr=True):
        stripped = line.strip()
        if count < 4 and stripped:  # TODO make the chunking size configurable
            lines.append(stripped)
            count += 1
        else:
            log_task_status(task, [f"[{task.agent.name}] {line}" for line in lines])
            lines = []
            count = 0

    task.status = TaskStatus.SUCCESS
    now = timezone.now()
    task.updated = now
    task.completed = now
    task.save()


def submit_jobqueue_task(task: Task, ssh: SSH) -> str:
    precommand = '; '.join(str(task.agent.pre_commands).splitlines()) if task.agent.pre_commands else ':'
    command = f"sbatch {task.guid}.sh"
    workdir = join(task.agent.workdir, task.workdir)

    lines = []
    for line in execute_command(ssh=ssh, precommand=precommand, command=command, directory=workdir, allow_stderr=True):
        stripped = line.strip()
        if stripped:
            log_task_status(task, [f"[{task.agent.name}] {stripped}"])
            lines.append(stripped)

    job_id = parse_task_job_id(lines[-1])
    task.job_id = job_id
    task.updated = timezone.now()
    task.save()

    return job_id


def log_task_status(task: Task, messages: List[str]):
    log_path = join(environ.get('RUNS_LOGS'), f"{task.guid}.plantit.log")
    with open(log_path, 'a') as log:
        for message in messages:
            logger.info(f"[Task {task.guid} ({task.user.username}/{task.name})] {message}")
            log.write(f"{message}\n")


async def push_task_event(task: Task):
    user = await get_task_user(task)
    await get_channel_layer().group_send(f"tasks-{user.username}", {
        'type': 'task_event',
        'task': await sync_to_async(task_to_dict)(task),
    })


def cancel_task(task: Task, auth):
    ssh = get_task_ssh_client(task, auth)
    with ssh:
        if isinstance(task, JobQueueTask):
            lines = []
            for line in execute_command(
                    ssh=ssh,
                    precommand=':',
                    command=f"squeue -u {task.agent.username}",
                    directory=join(task.agent.workdir, task.workdir)):
                logger.info(line)
                lines.append(line)

            if task.job_id is None or not any([task.job_id in r for r in lines]):
                return  # run doesn't exist, so no need to cancel

            execute_command(
                ssh=ssh,
                precommand=':',
                command=f"scancel {task.job_id}",
                directory=join(task.agent.workdir, task.workdir))


def get_task_orchestration_log_file_path(task: Task):
    return join(os.environ.get('RUNS_LOGS'), f"{task.guid}.plantit.log")


def get_task_container_log_file_name(task: Task):
    if isinstance(task, JobQueueTask) and task.agent.launcher:
        return f"plantit.{task.job_id}.out"
    else:
        return f"{task.guid}.{task.agent.name.lower()}.log"


def get_task_container_log_file_path(task: Task):
    return join(os.environ.get('RUNS_LOGS'), get_task_container_log_file_name(task))


def get_task_container_logs(task: Task, ssh: SSH):
    work_dir = join(task.agent.workdir, task.workdir)
    container_log_file = get_task_container_log_file_name(task)
    container_log_path = get_task_container_log_file_path(task)

    with ssh:
        with ssh.client.open_sftp() as sftp:
            cmd = 'test -e {0} && echo exists'.format(join(work_dir, container_log_file))
            stdin, stdout, stderr = ssh.client.exec_command(cmd)

            if not stdout.read().decode().strip() == 'exists':
                container_logs = []
            else:
                with open(get_task_container_log_file_path(task), 'a+') as log_file:
                    sftp.chdir(work_dir)
                    sftp.get(container_log_file, log_file.name)

                # obfuscate Docker auth info before returning logs to the user
                docker_username = environ.get('DOCKER_USERNAME', None)
                docker_password = environ.get('DOCKER_PASSWORD', None)
                for line in fileinput.input([container_log_path], inplace=True):
                    if docker_username in line.strip():
                        line = line.strip().replace(docker_username, '*' * 7, 1)
                    if docker_password in line.strip():
                        line = line.strip().replace(docker_password, '*' * 7)
                    sys.stdout.write(line)


def stat_task_orchestration_logs(guid: str):
    log_path = Path(join(environ.get('TASKS_LOGS'), f"{guid}.plantit.log"))
    return datetime.fromtimestamp(log_path.stat().st_mtime) if log_path.is_file() else None


def remove_task_orchestration_logs(guid: str):
    local_log_path = join(environ.get('TASKS_LOGS'), f"{guid}.plantit.log")
    os.remove(local_log_path)


def get_jobqueue_task_job_walltime(task: JobQueueTask) -> (str, str):
    ssh = SSH(task.agent.hostname, task.agent.port, task.agent.username)
    with ssh:
        lines = execute_command(
            ssh=ssh,
            precommand=":",
            command=f"squeue --user={task.agent.username}",
            directory=join(task.agent.workdir, task.workdir),
            allow_stderr=True)

        try:
            job_line = next(l for l in lines if task.job_id in l)
            job_split = job_line.split()
            job_walltime = job_split[-3]
            return job_walltime
        except StopIteration:
            return None


def get_jobqueue_task_job_status(task: JobQueueTask) -> str:
    ssh = SSH(task.agent.hostname, task.agent.port, task.agent.username)
    with ssh:
        lines = execute_command(
            ssh=ssh,
            precommand=':',
            command=f"sacct -j {task.job_id}",
            directory=join(task.agent.workdir, task.workdir),
            allow_stderr=True)

        job_line = next(l for l in lines if task.job_id in l)
        job_split = job_line.split()
        job_status = job_split[5].replace('+', '')
        return job_status
    pass


def get_task_result_files(task: Task, workflow: dict, auth: dict) -> List[dict]:
    included_by_name = ((workflow['output']['include']['names'] if 'names' in workflow['output'][
        'include'] else [])) if 'output' in workflow else []  # [f"{run.task_id}.zip"]
    included_by_name.append(f"{task.guid}.zip")  # zip file
    if not task.agent.launcher:
        included_by_name.append(f"{task.guid}.{task.agent.name.lower()}.log")
    if isinstance(task, JobQueueTask) and task.job_id is not None and task.job_id != '':
        included_by_name.append(f"plantit.{task.job_id}.out")
        included_by_name.append(f"plantit.{task.job_id}.err")
    included_by_pattern = (
        workflow['output']['include']['patterns'] if 'patterns' in workflow['output']['include'] else []) if 'output' in workflow else []

    ssh = get_task_ssh_client(task, auth)
    workdir = join(task.agent.workdir, task.workdir)
    outputs = []
    seen = []

    with ssh:
        with ssh.client.open_sftp() as sftp:
            for file in included_by_name:
                file_path = join(workdir, file)
                stdin, stdout, stderr = ssh.client.exec_command(f"test -e {file_path} && echo exists")
                output = {
                    'name': file,
                    'path': join(workdir, file),
                    'exists': stdout.read().decode().strip() == 'exists'
                }
                seen.append(output['name'])
                outputs.append(output)

            for f in sftp.listdir(workdir):
                if any(pattern in f for pattern in included_by_pattern):
                    if not any(s == f for s in seen):
                        outputs.append({
                            'name': f,
                            'path': join(workdir, f),
                            'exists': True
                        })

    return outputs


def list_task_input_files(task: Task, options: PlantITCLIOptions) -> List[str]:
    input_files = terrain.list_dir(options['input']['path'], task.user.profile.cyverse_access_token)
    msg = f"Found {len(input_files)} input file(s)"
    log_task_status(task, msg)
    async_to_sync(push_task_event)(task)
    logger.info(msg)

    return input_files


def get_task_ssh_client(task: Task, auth: dict) -> SSH:
    username = auth['username']
    if 'password' in auth:
        logger.info(f"Using password authentication (username: {username})")
        client = SSH(host=task.agent.hostname, port=task.agent.port, username=username, password=auth['password'])
    elif 'path' in auth:
        logger.info(f"Using key authentication (username: {username})")
        client = SSH(host=task.agent.hostname, port=task.agent.port, username=task.agent.username, pkey=auth['path'])
    else:
        raise ValueError(f"Unrecognized authentication strategy")

    return client


def parse_task_auth_options(auth: dict) -> dict:
    if 'password' in auth:
        return PasswordTaskAuth(username=auth['username'], password=auth['password'])
    else:
        return KeyTaskAuth(username=auth['username'], path=str(get_user_private_key_path(auth['username'])))


def task_to_dict(task: Task) -> dict:
    task_log_file = get_task_orchestration_log_file_path(task)

    if Path(task_log_file).is_file():
        with open(task_log_file, 'r') as log:
            task_logs = [line.strip() for line in log.readlines()[-int(1000000):]]
    else:
        task_logs = []

    try:
        AgentAccessPolicy.objects.get(user=task.user, agent=task.agent, role__in=[AgentRole.admin, AgentRole.guest])
        can_restart = True
    except:
        can_restart = False

    results = RedisClient.get().get(f"results/{task.guid}")

    t = {
        'can_restart': can_restart,
        'guid': task.guid,
        'status': task.status,
        'owner': task.user.username,
        'name': task.name,
        'work_dir': task.workdir,
        'task_logs': task_logs,
        'agent': task.agent.name if task.agent is not None else None,
        'created': task.created.isoformat(),
        'updated': task.updated.isoformat(),
        'completed': task.completed.isoformat() if task.completed is not None else None,
        'workflow_owner': task.workflow_owner,
        'workflow_name': task.workflow_name,
        'tags': [str(tag) for tag in task.tags.all()],
        'is_complete': task.is_complete,
        'is_success': task.is_success,
        'is_failure': task.is_failure,
        'is_cancelled': task.is_cancelled,
        'is_timeout': task.is_timeout,
        'workflow_image_url': task.workflow_image_url,
        'result_previews_loaded': task.previews_loaded,
        'cleaned_up': task.cleaned_up,
        'output_files': json.loads(results) if results is not None else []
    }

    if isinstance(task, JobQueueTask):
        t['job_id'] = task.job_id
        t['job_status'] = task.job_status
        t['job_walltime'] = task.job_elapsed_walltime

    return t


def delayed_task_to_dict(task: DelayedTask) -> dict:
    return {
        'agent': agent_to_dict(task.agent),
        'name': task.name,
        'eta': task.eta,
        'interval': {
            'every': task.interval.every,
            'period': task.interval.period
        },
        'last_run': task.last_run_at
    }


def repeating_task_to_dict(task: RepeatingTask):
    return {
        'agent': agent_to_dict(task.agent),
        'name': task.name,
        'eta': task.eta,
        'interval': {
            'every': task.interval.every,
            'period': task.interval.period
        },
        'enabled': task.enabled,
        'last_run': task.last_run_at
    }


# notifications

def notification_to_dict(notification: Notification) -> dict:
    # if isinstance(notification, DirectoryPolicyNotification):
    #     return map_directory_policy_notification(notification)
    # else:
    return {
        'id': notification.guid,
        'username': notification.user.username,
        'created': notification.created.isoformat(),
        'message': notification.message,
        'read': notification.read,
    }


# def map_directory_policy_notification(notification: DirectoryPolicyNotification):
#     return {
#         'id': notification.guid,
#         'username': notification.user.username,
#         'created': notification.created.isoformat(),
#         'message': notification.message,
#         'read': notification.read,
#         'policy': dataset_access_policy_to_dict(notification.policy)
#     }


# datasets

def dataset_access_policy_to_dict(policy: DatasetAccessPolicy):
    return {
        'owner': policy.owner.username,
        'guest': policy.guest.username,
        'path': policy.path,
        'role': policy.role.value
    }


# def map_dataset_session(session: DatasetSession):
#     log_path = join(environ.get('SESSIONS_LOGS'), f"{session.guid}.session.log")
#     if Path(log_path).exists():
#         with open(log_path, 'r') as file:
#             lines = file.readlines()
#     else:
#         lines = []
#
#     return {
#         'guid': session.guid,
#         'path': session.path,
#         'workdir': session.workdir,
#         'agent': session.agent.name,
#         'modified': session.modified if session.modified is not None else [],
#         'output': lines,
#         'opening': session.opening
#     }
#
#
# def update_dataset_session(session: DatasetSession, output: List[str]):
#     log_path = join(environ.get('SESSIONS_LOGS'), f"{session.guid}.session.log")
#     with open(log_path, 'a') as log:
#         for line in output:
#             log.write(f"{line}\n")
#
#     if session.channel_name is not None:
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.send)(session.channel_name, {
#             'type': 'update.session',
#             'session': map_dataset_session(session),
#         })


# agents

@sync_to_async
def get_agent_user(agent: Agent):
    return agent.user


@sync_to_async
def agent_to_dict_async(agent: Agent, user: User = None):
    return agent_to_dict(agent, user)


def agent_to_dict(agent: Agent, user: User = None) -> dict:
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
        'tasks': [agent_task_to_dict(task) for task in tasks],
        'logo': agent.logo,
        'authentication': agent.authentication,
        'users_authorized': [{
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            } for user in users_authorized if user is not None],
        'workflows_authorized': [json.loads(redis.get(f"workflows/{workflow.repo_owner}/{workflow.repo_name}")) for workflow in workflows_authorized],
        'workflows_blocked': [json.loads(redis.get(f"workflows/{workflow.repo_owner}/{workflow.repo_name}")) for workflow in workflows_blocked]
    }

    if agent.user is not None: mapped['user'] = agent.user.username
    return mapped


def agent_task_to_dict(task: AgentTask) -> dict:
    return {
        'name': task.name,
        'description': task.description,
        'command': task.command,
        'crontab': str(task.crontab).rpartition("(")[0].strip(),
        'enabled': task.enabled,
        'last_run': task.last_run_at
    }


def has_virtual_memory(agent: Agent) -> bool:
    return agent.header_skip == '--mem'
