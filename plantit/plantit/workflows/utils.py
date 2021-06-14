import asyncio
import json
import logging
from datetime import datetime
from typing import List

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

from plantit.github import list_connectable_repos_by_owner, get_repo_bundle
from plantit.redis import RedisClient
from plantit.users.utils import get_django_profile
from plantit.workflows.models import Workflow

logger = logging.getLogger(__name__)


@sync_to_async
def filter_workflows(user: User = None, public: bool = None):
    workflows = Workflow.objects.all()
    if user is not None: workflows = workflows.filter(user=user)
    if public is not None: workflows = workflows.filter(public=public)
    return list(workflows)


@sync_to_async
def get_workflow_user(workflow: Workflow):
    return workflow.user


async def bind_workflow_bundle(workflow: Workflow, token: str) -> dict:
    bundle = await get_repo_bundle(
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


async def repopulate_personal_workflow_bundle_cache(owner: str):
    try:
        user = await sync_to_async(User.objects.get)(profile__github_username=owner)
    except:
        logger.warning(f"User {owner} does not exist")
        return

    empty_personal_workflow_bundle_cache(owner)

    profile = await get_django_profile(user)
    owned = await filter_workflows(user=user)
    bind = asyncio.gather(*[bind_workflow_bundle(workflow, profile.github_token) for workflow in owned])
    tasks = await asyncio.gather(*[bind, list_connectable_repos_by_owner(owner, profile.github_token)])
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
    for workflow in both: redis.set(f"workflows/{owner}/{workflow['repo']['name']}", json.dumps(workflow))
    redis.set(f"workflows_updated/{owner}", timezone.now().timestamp())
    logger.info(f"Added {len(bound)} bound, {len(bindable) - len(bound)} bindable, {len(both)} total to {owner}'s workflow cache" + ("" if missing == 0 else f"({missing} with missing configuration files)"))


async def repopulate_public_workflow_bundle_cache(token: str):
    redis = RedisClient.get()
    public_workflows = await filter_workflows(public=True)
    encountered_users = []

    for workflow, user in list(zip(public_workflows, [await get_workflow_user(workflow) for workflow in public_workflows])):
        if user is None:
            # workflow is not owned by any particular user (e.g., added by admins for shared GitHub group) so explicitly refresh the binding
            logger.info(f"Binding unclaimed workflow {workflow.repo_owner}/{workflow.repo_name}")
            bundle = await bind_workflow_bundle(workflow, token)
            redis.set(f"workflows/{workflow.repo_owner}/{workflow.repo_name}", json.dumps(bundle))
        else:
            # otherwise refresh all the workflow owner's workflows (but only once)
            if user.username in encountered_users: continue
            profile = await get_django_profile(user)
            empty_personal_workflow_bundle_cache(profile.github_username)
            await repopulate_personal_workflow_bundle_cache(profile.github_username)
            encountered_users.append(user.username)

    redis.set(f"public_workflows_updated", timezone.now().timestamp())


async def get_public_workflow_bundles(token: str, invalidate: bool = False) -> List[dict]:
    redis = RedisClient.get()
    updated = redis.get('public_workflows_updated')

    # repopulate if empty or invalidation requested
    if updated is None or len(list(redis.scan_iter(match=f"workflows/*"))) == 0 or invalidate:
        logger.info(f"Populating public workflow cache")
        await repopulate_public_workflow_bundle_cache(token)
    else:
        age = (datetime.now() - datetime.fromtimestamp(float(updated)))
        age_secs = age.total_seconds()
        max_secs = (int(settings.WORKFLOWS_REFRESH_MINUTES) * 60)

        # otherwise only if stale
        if age_secs > max_secs:
            logger.info(f"Public workflow cache is stale ({age_secs}s old, {age_secs - max_secs}s past limit), repopulating")
            await repopulate_public_workflow_bundle_cache(token)

    workflows = [json.loads(redis.get(key)) for key in redis.scan_iter(match='workflows/*')]
    return [workflow for workflow in workflows if workflow['public']]


async def get_personal_workflow_bundles(owner: str, invalidate: bool = False) -> List[dict]:
    redis = RedisClient.get()
    updated = redis.get(f"workflows_updated/{owner}")

    # repopulate if empty or invalidation requested
    if updated is None or len(list(redis.scan_iter(match=f"workflows/{owner}/*"))) == 0 or invalidate:
        await repopulate_personal_workflow_bundle_cache(owner)
    else:
        age = (datetime.now() - datetime.fromtimestamp(float(updated)))
        age_secs = age.total_seconds()
        max_secs = (int(settings.WORKFLOWS_REFRESH_MINUTES) * 60)

        # otherwise only if stale
        if age_secs > max_secs:
            logger.info(f"GitHub user {owner}'s workflow cache is stale ({age_secs}s old, {age_secs - max_secs}s past limit), repopulating")
            await repopulate_personal_workflow_bundle_cache(owner)

    return [json.loads(redis.get(key)) for key in redis.scan_iter(match=f"workflows/{owner}/*")]


async def get_workflow_bundle(owner: str, name: str, token: str, invalidate: bool = False) -> dict:
    redis = RedisClient.get()
    updated = redis.get(f"workflows_updated/{owner}")
    workflow = redis.get(f"workflows/{owner}/{name}")

    if updated is None or workflow is None or invalidate:
        try: workflow = await sync_to_async(Workflow.objects.get)(repo_owner=owner, repo_name=name)
        except: raise ValueError(f"Workflow {owner}/{name} not found")

        workflow = await bind_workflow_bundle(workflow, token)
        redis.set(f"workflows/{owner}/{name}", json.dumps(workflow))

    return workflow


def empty_personal_workflow_bundle_cache(owner: str):
    redis = RedisClient.get()
    keys = list(redis.scan_iter(match=f"workflows/{owner}/*"))
    cleaned = len(keys)
    for key in keys: redis.delete(key)
    logger.info(f"Emptied {cleaned} workflows from GitHub user {owner}'s cache")
    return cleaned
