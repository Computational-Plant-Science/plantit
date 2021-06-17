import json
import logging
import subprocess
from datetime import timedelta
from os.path import join
from pathlib import Path

import numpy as np
import requests
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth.models import User

import plantit.terrain as terrain
import plantit.github as github
from plantit.redis import RedisClient
from plantit.tasks.models import Task
from plantit.workflows.models import Workflow

logger = logging.getLogger(__name__)


def list_users(github_token: str):
    # TODO factor out cache updating
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
    return [json.loads(redis.get(key)) for key in redis.scan_iter(match='users/*')]


@sync_to_async
def get_django_profile(user: User):
    return user.profile


def get_cyverse_profile(user: User) -> dict:
    profile = terrain.get_profile(user.username, user.profile.cyverse_access_token)
    altered = False
    if profile['first_name'] != user.first_name: user.first_name = profile['first_name']
    if profile['last_name'] != user.last_name: user.last_name = profile['last_name']
    if altered: user.save()

    return profile


def refresh_cyverse_tokens(user: User):
    access_token, refresh_token = terrain.refresh_tokens(username=user.username, refresh_token=user.profile.cyverse_refresh_token)
    user.profile.cyverse_access_token = access_token
    user.profile.cyverse_refresh_token = refresh_token
    user.profile.save()
    user.save()


async def get_github_profile(user: User):
    profile = await get_django_profile(user)
    return await github.get_profile(profile.github_username, profile.github_token)


def get_or_create_keypair(owner: str, overwrite: bool = False) -> str:
    """
    Creates an RSA-protected SSH keypair for the user and returns the public key (or gets the public key if a keypair already exists).
    To overwrite a pre-existing keypair, use the `invalidate` argument.

    Args:
        owner: The user (CyVerse/Django username) to create a keypair for.
        overwrite: Whether to overwrite an existing keypair.

    Returns: The path to the newly created public key.
    """
    public_key_path = get_public_key_path(owner)
    private_key_path = get_private_key_path(owner)

    if public_key_path.is_file():
        if overwrite:
            logger.info(f"Keypair for {owner} already exists, overwriting")
            public_key_path.unlink()
            private_key_path.unlink(missing_ok=True)
        else:
            logger.info(f"Keypair for {owner} already exists")
    else:
        subprocess.run(f"ssh-keygen -b 2048 -t rsa -f {private_key_path} -N \"\"", shell=True)
        logger.info(f"Created keypair for {owner}")

    with open(public_key_path, 'r') as key:
        return key.readlines()[0]


def get_private_key_path(owner: str) -> Path:
    keys_path = Path(settings.AGENT_KEYS)
    owner_keys_path = Path(f"{keys_path.absolute()}/{owner}")
    owner_keys_path.mkdir(exist_ok=True, parents=True)
    return Path(join(owner_keys_path, f"{owner}_id_rsa"))


def get_public_key_path(owner: str) -> Path:
    keys_path = Path(settings.AGENT_KEYS)
    owner_keys_path = Path(f"{keys_path.absolute()}/{owner}")
    owner_keys_path.mkdir(exist_ok=True, parents=True)
    return Path(join(owner_keys_path, f"{owner}_id_rsa.pub"))


def get_user_statistics(user: User) -> dict:
    all_tasks = Task.objects.filter(user=user)
    completed_tasks = list(Task.objects.filter(user=user, completed__isnull=False))

    total_tasks = all_tasks.count()
    total_time = sum([(task.completed - task.created).total_seconds() for task in completed_tasks])
    total_results = sum([len(task.results if task.results is not None else []) for task in completed_tasks])
    owned_workflows = len(Workflow.objects.filter(user=user))
    used_workflows = len(np.unique([f"{task.workflow_owner}/{task.workflow_name}" for task in all_tasks]))

    return {
        'total_tasks': total_tasks,
        'total_task_seconds': total_time,
        'total_task_results': total_results,
        'owned_workflows': owned_workflows,
        'used_workflows': used_workflows
    }
