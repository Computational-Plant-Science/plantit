import json
import logging
from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import List

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned
from django.utils import timezone
from redis import Redis

from plantit.filters import filter_online_users, workflow_is_featured
from plantit.github import GitHubClient, AsyncGitHubClient, GitHubViews, AsyncGitHubViews
from plantit.miappe.models import Investigation
from plantit.misc.models import FeaturedWorkflow
from plantit.serialize import project_to_dict
from plantit.bundle import get_user_bundle
from plantit.users.models import Profile
from plantit.utils.misc import del_none


class CacheViews(metaclass=ABCMeta):
    @abstractmethod
    def is_stale(self, pattern: str):
        pass

    @abstractmethod
    def get_users(self, invalidate: bool = False):
        pass

    @abstractmethod
    def get_user_workflows(self, user: User):
        pass

    @abstractmethod
    def get_project_workflows(self, project: Investigation):
        pass

    @abstractmethod
    def get_public_workflows(self):
        pass

    @abstractmethod
    def get_workflows(self, github_login: str, github_token: str, organization: bool = False, invalidate: bool = False):
        pass


class RedisCacheViews(CacheViews):
    def __init__(self, client: Redis):
        super(RedisCacheViews, self).__init__()
        self.__logger = logging.getLogger(RedisCacheViews.__name__)
        self.__client = client

    def is_stale(self, pattern: str):
        matches = list(self.__client.scan_iter(match=pattern))
        updated = self.__client.get(f"{pattern.strip().replace('/', '').replace('*', '')}_updated")

        if matches is None:
            self.__logger.warning(f"Pattern '{pattern}' not found in cache")
            raise ValueError(f"")

        if updated is None:
            self.__logger.info(f"Cache pattern '{pattern}' is stale (never been updated)")
            return True

        age = (datetime.now() - datetime.fromtimestamp(float(updated)))
        age_secs = age.total_seconds()
        max_secs = (int(settings.USERS_REFRESH_MINUTES) * 60)
        stale = age_secs > max_secs
        self.__logger.info(f"Cache pattern '{pattern}' is " + (f"stale ({age_secs}s old, {age_secs - max_secs}s past expiry)" if stale
                                                               else f"fresh ({age_secs}s old, {max_secs - age_secs}s until expiry)"))
        return stale

    def get_users(self, invalidate: bool = False):
        pattern = "users/*"
        matches = list(self.__client.scan_iter(match=pattern))

        # refresh if empty, stale, or invalidation requested
        if len(matches) == 0 or self.is_stale(pattern) or invalidate:
            self.__refresh_user_cache()

        return [json.loads(self.__client.get(match)) for match in matches]

    def get_workflows(self, github_login: str, github_token: str, organization: bool = False, invalidate: bool = False):
        pass

    def __refresh_user_cache(self):
        self.__logger.info(f"Refreshing user cache")
        for user in list(User.objects.all().exclude(profile__isnull=True)):
            bundle = get_user_bundle(user)
            self.__client.set(f"users/{user.username}", json.dumps(bundle))
        self.__client.set(f"users_updated", timezone.now().timestamp())

    def __refresh_user_workflow_cache(self, login: str):
        if login is None or login == '':
            raise ValueError(f"No GitHub username provided")

        try:
            profile = Profile.objects.get(github_username=login)
            user = profile.user
        except MultipleObjectsReturned:
            self.__logger.warning(f"Multiple users bound to Github user {login}!")
            return
        except:
            self.__logger.warning(f"Github user {login} does not exist")
            return

        # scrape GitHub to synchronize repos and workflow config
        profile = Profile.objects.get(user=user)
        github = GitHubViews(profile.github_token)
        workflows = github.get_connectable_workflows(login)

        # update the cache, first removing workflows that no longer exist
        removed = 0
        updated = 0
        added = 0
        old_keys = [key.decode('utf-8') for key in self.__client.scan_iter(match=f"workflows/{login}/*")]
        new_keys = [f"workflows/{login}/{wf['repo']['name']}/{wf['branch']['name']}" for wf in workflows]
        for old_key in old_keys:
            # invalidate submission config cache
            config_key = f"workflow_configs/{user.username}/{old_key.partition('/')[2]}"
            if self.__client.exists(config_key):
                self.__logger.info(f"Removing cached workflow configuration {config_key}")
                self.__client.delete(config_key)

            if old_key not in new_keys:
                self.__logger.debug(f"Removing user workflow {old_key}")
                removed += 1
                self.__client.delete(old_key)
            else:
                self.__logger.debug(f"Updating user workflow {old_key}")
                updated += 1

        # ...then adding/updating the workflows we just scraped
        for wf in workflows:
            # set flag if this is a featured workflow
            wf['featured'] = workflow_is_featured(login, wf['repo']['name'], wf['branch']['name'])

            key = f"workflows/{login}/{wf['repo']['name']}/{wf['branch']['name']}"
            if key not in old_keys:
                self.__logger.debug(f"Adding user workflow {key}")
                added += 1
            self.__client.set(key, json.dumps(del_none(wf)))

        self.__client.set(f"workflows_updated/{login}", timezone.now().timestamp())
        self.__logger.info(
            f"{len(workflows)} workflow(s) now in GitHub user's {login}'s workflow cache (added {added}, updated {updated}, removed {removed})")

    def __refresh_org_workflow_cache(self, org_name: str, github_token: str):
        # scrape GitHub to synchronize repos and workflow config
        github = GitHubViews(github_token)
        workflows = github.get_connectable_workflows(org_name)

        # update the cache, first removing workflows that no longer exist
        removed = 0
        updated = 0
        added = 0
        old_keys = [key.decode('utf-8') for key in self.__client.scan_iter(match=f"workflows/{org_name}/*")]
        new_keys = [f"workflows/{org_name}/{wf['repo']['name']}/{wf['branch']['name']}" for wf in workflows]
        for old_key in old_keys:
            if old_key not in new_keys:
                self.__logger.debug(f"Removing org workflow {old_key}")
                removed += 1
                self.__client.delete(old_key)
            else:
                self.__logger.debug(f"Updating org workflow {old_key}")
                updated += 1

        # ...then adding/updating the workflows we just scraped
        for wf in workflows:
            # set flag if this is a featured workflow
            wf['featured'] = await workflow_is_featured(org_name, wf['repo']['name'], wf['branch']['name'])

            key = f"workflows/{org_name}/{wf['repo']['name']}/{wf['branch']['name']}"
            if key not in old_keys:
                self.__logger.debug(f"Adding org workflow {key}")
                added += 1
            self.__client.set(key, json.dumps(del_none(wf)))

        self.__client.set(f"workflows_updated/{org_name}", timezone.now().timestamp())
        self.__logger.info(
            f"{len(workflows)} workflow(s) now in GitHub organization {org_name}'s workflow cache (added {added}, updated {updated}, removed {removed})")


def refresh_online_user_orgs_workflow_cache():
    users = User.objects.all()
    online = filter_online_users(users)
    for user in online:
        profile = Profile.objects.get(user=user)
        github_organizations = get_member_organizations(user)
        logger.info(f"Refreshing workflow cache for online user {user.username}'s {len(online)} organizations")
        for org in github_organizations:
            refresh_org_workflow_cache(org['login'], profile.github_token)



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

    if workflow is None or self.is_stale() invalidate:
        github = GitHubViews(github_token)
        workflow = github.get_workflow_bundle(owner, name, branch)
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
        bundle = await github.get_repo_bundle(owner, name, branch, github_token)
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
