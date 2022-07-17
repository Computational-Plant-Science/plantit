import json
import logging
from datetime import datetime
from typing import List

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned
from django.utils import timezone

from plantit.filters import filter_online_users, is_featured
from plantit.github import GitHubClient, get_user_github_organizations, AsyncGitHubClient
from plantit.miappe.models import Investigation
from plantit.misc.models import FeaturedWorkflow
from plantit.serialize import project_to_dict
from plantit.bundle import get_user_bundle
from plantit.redis import RedisClient
from plantit.users.models import Profile
from plantit.utils.misc import del_none

logger = logging.getLogger(__name__)


def refresh_online_users_workflow_cache():
    users = User.objects.all()
    online = filter_online_users(users)
    logger.info(f"Refreshing workflow cache for {len(online)} online user(s)")
    for user in online:
        profile = Profile.objects.get(user=user)
        username = profile.github_username
        if username is not None and username != '':
            refresh_user_workflow_cache(profile.github_username)


def refresh_user_workflow_cache(github_username: str):
    if github_username is None or github_username == '': raise ValueError(f"No GitHub username provided")

    try:
        profile = Profile.objects.get(github_username=github_username)
        user = profile.user
    except MultipleObjectsReturned:
        logger.warning(f"Multiple users bound to Github user {github_username}!")
        return
    except:
        logger.warning(f"Github user {github_username} does not exist")
        return

    # scrape GitHub to synchronize repos and workflow config
    profile = Profile.objects.get(user=user)
    github = GitHubClient(profile.github_token)
    workflows = github.list_connectable_repos_by_owner(github_username)

    # update the cache, first removing workflows that no longer exist
    redis = RedisClient.get()
    removed = 0
    updated = 0
    added = 0
    old_keys = [key.decode('utf-8') for key in redis.scan_iter(match=f"workflows/{github_username}/*")]
    new_keys = [f"workflows/{github_username}/{wf['repo']['name']}/{wf['branch']['name']}" for wf in workflows]
    for old_key in old_keys:
        # invalidate submission config cache
        config_key = f"workflow_configs/{user.username}/{old_key.partition('/')[2]}"
        if redis.exists(config_key):
            logger.info(f"Removing cached workflow configuration {config_key}")
            redis.delete(config_key)

        if old_key not in new_keys:
            logger.debug(f"Removing user workflow {old_key}")
            removed += 1
            redis.delete(old_key)
        else:
            logger.debug(f"Updating user workflow {old_key}")
            updated += 1

    # ...then adding/updating the workflows we just scraped
    for wf in workflows:
        # set flag if this is a featured workflow
        wf['featured'] = is_featured(github_username, wf['repo']['name'], wf['branch']['name'])

        key = f"workflows/{github_username}/{wf['repo']['name']}/{wf['branch']['name']}"
        if key not in old_keys:
            logger.debug(f"Adding user workflow {key}")
            added += 1
        redis.set(key, json.dumps(del_none(wf)))

    redis.set(f"workflows_updated/{github_username}", timezone.now().timestamp())
    logger.info(
        f"{len(workflows)} workflow(s) now in GitHub user's {github_username}'s workflow cache (added {added}, updated {updated}, removed {removed})")


def refresh_online_user_orgs_workflow_cache():
    users = User.objects.all()
    online = filter_online_users(users)
    for user in online:
        profile = Profile.objects.get(user=user)
        github_organizations = get_user_github_organizations(user)
        logger.info(f"Refreshing workflow cache for online user {user.username}'s {len(online)} organizations")
        for org in github_organizations:
            await refresh_org_workflow_cache(org['login'], profile.github_token)


def refresh_org_workflow_cache(org_name: str, github_token: str):
    # scrape GitHub to synchronize repos and workflow config
    github = GitHubClient(github_token)
    workflows = github.list_connectable_repos_by_org(org_name)

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
        # set flag if this is a featured workflow
        wf['featured'] = await is_featured(org_name, wf['repo']['name'], wf['branch']['name'])

        key = f"workflows/{org_name}/{wf['repo']['name']}/{wf['branch']['name']}"
        if key not in old_keys:
            logger.debug(f"Adding org workflow {key}")
            added += 1
        redis.set(key, json.dumps(del_none(wf)))

    redis.set(f"workflows_updated/{org_name}", timezone.now().timestamp())
    logger.info(
        f"{len(workflows)} workflow(s) now in GitHub organization {org_name}'s workflow cache (added {added}, updated {updated}, removed {removed})")


def refresh_user_cache():
    logger.info(f"Refreshing user cache")
    redis = RedisClient.get()
    for user in list(User.objects.all().exclude(profile__isnull=True)):
        bundle = get_user_bundle(user)
        redis.set(f"users/{user.username}", json.dumps(bundle))
    RedisClient.get().set(f"users_updated", timezone.now().timestamp())


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


def list_public_workflows() -> List[dict]:
    redis = RedisClient.get()
    workflows = [wf for wf in [json.loads(redis.get(key)) for key in redis.scan_iter(match='workflows/*')] if
                 'public' in wf['config'] and wf['config']['public']]
    return workflows


def list_user_workflows(owner: str) -> List[dict]:
    redis = RedisClient.get()
    return [json.loads(redis.get(key)) for key in redis.scan_iter(match=f"workflows/{owner}/*")]


def get_project_workflows(project: Investigation):
    redis = RedisClient.get()
    workflows = [wf for wf in [json.loads(redis.get(key)) for key in redis.scan_iter(match='workflows/*')] if
                 'projects' in wf['config'] and project.guid in wf['config']['projects']]
    return workflows


def list_org_workflows(organization: str) -> List[dict]:
    redis = RedisClient.get()
    return [json.loads(redis.get(key)) for key in redis.scan_iter(match=f"workflows/{organization}/*")]


def list_project_workflows(project: Investigation) -> List[dict]:
    redis = RedisClient.get()
    proj_dict = project_to_dict(project)
    return [json.loads(wf) for wf in [redis.get(key) for key in [f"workflows/{name}" for name in proj_dict['workflows']]] if wf is not None]


def get_workflow(
        owner: str,
        name: str,
        branch: str,
        github_token: str,
        invalidate: bool = False) -> dict:
    redis = RedisClient.get()
    updated = redis.get(f"workflows_updated/{owner}")
    workflow = redis.get(f"workflows/{owner}/{name}/{branch}")

    if updated is None or workflow is None or invalidate:
        github = GitHubClient(github_token)
        bundle = github.get_repo_bundle(owner, name, branch)
        workflow = {
            'config': bundle['config'],
            'repo': bundle['repo'],
            'validation': bundle['validation'],
            'branch': branch,
            'featured': FeaturedWorkflow.objects.filter(owner=owner, name=name, branch=branch).exists()
        }
        redis.set(f"workflows/{owner}/{name}/{branch}", json.dumps(del_none(workflow)))
        return workflow
    else:
        return json.loads(workflow)


async def get_workflow_async(
        owner: str,
        name: str,
        branch: str,
        github_token: str,
        invalidate: bool = False) -> dict:
    redis = RedisClient.get()
    updated = redis.get(f"workflows_updated/{owner}")
    workflow = redis.get(f"workflows/{owner}/{name}/{branch}")

    if updated is None or workflow is None or invalidate:
        github = AsyncGitHubClient(github_token)
        bundle = await github.get_repo_bundle_async(owner, name, branch, github_token)
        workflow = {
            'config': bundle['config'],
            'repo': bundle['repo'],
            'validation': bundle['validation'],
            'branch': branch,
            'featured': FeaturedWorkflow.objects.filter(owner=owner, name=name, branch=branch).exists()
        }
        redis.set(f"workflows/{owner}/{name}/{branch}", json.dumps(del_none(workflow)))
        return workflow
    else:
        return json.loads(workflow)