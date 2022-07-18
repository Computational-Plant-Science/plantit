import json
import logging
from abc import ABCMeta, abstractmethod
from collections import Counter
from typing import List, Dict, Optional
from datetime import datetime

import numpy as np
from asgiref.sync import async_to_sync
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from redis import Redis

import plantit.statistics as statistics
import plantit.mapbox as mapbox
from plantit.agents.models import Agent
from plantit.bundle import get_user_bundle
from plantit.filters import workflow_is_featured, filter_user_projects, filter_online_users
from plantit.github import GitHubViews
from plantit.miappe.models import Investigation
from plantit.serialize import agent_to_dict, project_to_dict
from plantit.tasks.models import TaskCounter, Task, TaskStatus, DelayedTask, RepeatingTask, TriggeredTask
from plantit.users.models import Profile, ManagedFile
from plantit.utils.misc import del_none


class ManualCacheViews(metaclass=ABCMeta):
    @abstractmethod
    def get_users(self, invalidate: bool = False):
        pass

    @abstractmethod
    def get_user_workflows(self, user: User, invalidate: bool = False) -> List[dict]:
        pass

    @abstractmethod
    def get_public_workflows(self) -> List[dict]:
        pass

    @abstractmethod
    def get_project_workflows(self, project: Investigation, invalidate: bool = False) -> List[dict]:
        pass

    @abstractmethod
    def get_organization_workflows(self,
                                   user: User,
                                   organization: str,
                                   invalidate: bool = False) -> List[dict]:
        pass

    @abstractmethod
    def get_workflow(self,
                     owner: str,
                     repo: str,
                     branch: str,
                     invalidate: bool = False) -> dict:
        pass

    @abstractmethod
    def get_institutions(self, invalidate: bool = False) -> dict:
        pass

    @abstractmethod
    def get_total_counts(self, invalidate: bool = False) -> dict:
        pass

    @abstractmethod
    def get_aggregate_timeseries(self, invalidate: bool = False) -> dict:
        pass

    @abstractmethod
    def get_user_timeseries(self, user: User, invalidate: bool = False) -> dict:
        pass

    @abstractmethod
    def get_user_statistics(self, user: User, invalidate: bool = False) -> dict:
        pass

    @abstractmethod
    def get_workflow_usage_timeseries(self,
                                      owner: str,
                                      repo: str,
                                      branch: str,
                                      invalidate: bool = False) -> dict:
        pass


class CacheopsViews(metaclass=ABCMeta):
    @abstractmethod
    def get_agents(self, user: User) -> List[Agent]:
        pass

    @abstractmethod
    def get_online_users(self, users: List[User]) -> List[User]:
        pass

    @abstractmethod
    def get_managed_files(self, user: User, page: int = 1) -> List[ManagedFile]:
        pass

    @abstractmethod
    def get_user_projects(self, user: User) -> List[Investigation]:
        pass

    @abstractmethod
    def get_tasks(self, user: User, completed: bool = None) -> List[Task]:
        pass

    @abstractmethod
    def get_tasks_paged(self, user: User, page: int = 1, completed: Optional[bool] = None) -> List[Task]:
        pass

    @abstractmethod
    def get_delayed_tasks(self, user: User) -> List[DelayedTask]:
        pass

    @abstractmethod
    def get_repeating_tasks(self, user: User) -> List[RepeatingTask]:
        pass

    @abstractmethod
    def get_triggered_tasks(self, user: User) -> List[TriggeredTask]:
        pass

    @abstractmethod
    def workflow_is_featured(self, owner: str, name: str, branch: str) -> bool:
        pass


class ModelViews(CacheopsViews, ManualCacheViews):
    def __init__(self, cache: Redis):
        super(ModelViews, self).__init__()

        if cache is None:
            raise ValueError(f"Redis client must be provided")

        self.__logger = logging.getLogger(ModelViews.__name__)
        self.__cache = cache

    # public methods

    def get_users(self, invalidate: bool = False):
        pattern = "users/*"
        matches = list(self.__cache.scan_iter(match=pattern))

        if len(matches) == 0 or invalidate:
            self.__logger.info(f"Refreshing user cache")
            users = self.__get_users()
            for user in users:
                self.__cache.set(f"users/{user.username}", json.dumps(user))

        return [json.loads(self.__cache.get(match)) for match in matches]

    def get_user_workflows(self, user: User, invalidate: bool = False) -> List[dict]:
        login = user.profile.github_username
        token = user.profile.github_token

        if login is None or login == '':
            self.__logger.warning(f"User hasn't linked a GitHub account")
            return []

        if token is None or token == '':
            self.__logger.warning(f"User has no GitHub token")
            return []

        if invalidate:
            self.__update_user_workflow_cache(user=user)

        pattern = f"workflows/{login}/*"
        return [json.loads(self.__cache.get(key)) for key in self.__cache.scan_iter(match=pattern)]

    def get_public_workflows(self) -> List[dict]:
        pattern = 'workflows/*'
        return [wf for wf in [json.loads(self.__cache.get(key)) for key in self.__cache.scan_iter(match=pattern)]
                if 'public' in wf['config'] and wf['config']['public']]

    def get_project_workflows(self, project: Investigation, invalidate: bool = False):
        if invalidate:
            pass

        pattern = 'workflows/*'
        return [wf for wf in [json.loads(self.__cache.get(key)) for key in self.__cache.scan_iter(match=pattern)]
                if 'projects' in wf['config'] and project.guid in wf['config']['projects']]

    def get_organization_workflows(self, user: User, organization: str, invalidate: bool = False) -> List[dict]:
        login = user.profile.github_username
        token = user.profile.github_token

        if login is None or login == '':
            self.__logger.warning(f"User hasn't linked a GitHub account")
            return []

        if token is None or token == '':
            self.__logger.warning(f"User has no GitHub token")
            return []

        if invalidate:
            self.__update_organization_workflow_cache(user=user, organization=organization)

        pattern = f"workflows/{organization}/*"
        return [json.loads(self.__cache.get(key)) for key in self.__cache.scan_iter(match=pattern)]

    def get_user_project_workflows(self, user: User) -> Dict[str, List[dict]]:
        projects = filter_user_projects(user)
        return {project.guid: self.get_project_workflows(project) for project in projects}

    def get_user_org_workflows(self, user: User) -> Dict[str, List[dict]]:
        organizations = GitHubViews.get_member_organizations(user)
        workflows = dict()
        for org in organizations: workflows[org['login']] = self.get_organization_workflows(org['login'])
        return workflows

    def get_workflow(self,
                     login: str,
                     repo: str,
                     branch: str,
                     invalidate: bool = False) -> dict:
        pattern = f"workflows/{login}/{repo}/{branch}"
        workflow = self.__cache.get(pattern)

        if workflow is None or invalidate:
            github = GitHubViews(self.__user.profile.github_token)
            workflow = github.get_workflow_bundle(login, repo, branch)
            self.__cache.set(pattern, json.dumps(del_none(workflow)))
            return workflow
        else:
            return json.loads(workflow)

    def get_institutions(self, invalidate: bool = False) -> dict:
        cached = list(self.__cache.scan_iter(match=f"institutions/*"))
        institutions = dict()

        if invalidate:
            institutions = self.__get_institutions()
            for name, institution in institutions.items():
                self.__cache.set(f"institutions/{name}", json.dumps(institution))
        else:
            for institution in cached:
                if institution is not None:
                    institutions[institution.decode('utf-8')] = json.loads(self.__cache.get(institution))

        return institutions

    def get_total_counts(self, invalidate: bool = False) -> dict:
        pattern = "stats_counts"
        cached = self.__cache.get(pattern)

        if cached is None or invalidate:
            totals = self.__get_total_counts()
            self.__cache.set(pattern, json.dumps(totals))
        else:
            totals = json.loads(cached)

        return totals

    def get_aggregate_timeseries(self, invalidate: bool = False) -> dict:
        pattern = "total_timeseries"
        cached = self.__cache.get(pattern)

        if cached is None or invalidate:
            series = self.__get_aggregate_timeseries()
            self.__cache.set(pattern, json.dumps(series))
        else:
            series = json.loads(cached)

        return series

    def get_user_timeseries(self, user: User, invalidate: bool = False) -> dict:
        pattern = f"user_timeseries/{user.username}"
        cached = self.__cache.get(pattern)

        if cached is None or invalidate:
            series = self.__get_user_timeseries(user)
            self.__cache.set(pattern, json.dumps(series))
        else:
            series = json.loads(cached)

        return series

    def get_user_statistics(self, user: User, invalidate: bool = False) -> dict:
        pattern = f"stats/{user.username}"
        cached = self.__cache.get(pattern)

        if cached is None or invalidate:
            stats = self.__get_user_statistics(user=user)
            self.__cache.set(pattern, json.dumps(stats))
        else:
            stats = json.loads(cached)

        return stats

    def get_workflow_usage_timeseries(self, owner: str, repo: str, branch: str, invalidate: bool = False) -> dict:
        pattern = f"workflow_timeseries/{owner}/{repo}/{branch}"
        cached = self.__cache.get(pattern)

        if cached is None or invalidate:
            series = self.__get_workflow_usage_timeseries(owner=owner, repo=repo, branch=branch)
            self.__cache.set(pattern, json.dumps(series))
        else:
            series = json.loads(cached)

        return series

    # internal methods

    def __get_users(self):
        users = [get_user_bundle(user) for user in list(User.objects.all().exclude(profile__isnull=True))]
        self.__logger.info(f"Current user count: {len(users)}")
        return users

    def __update_user_workflow_cache(self, user: User):
        login = user.profile.github_username
        token = user.profile.github_token

        if login is None or login == '':
            self.__logger.warning(f"User hasn't linked a GitHub account")
            return

        if token is None or token == '':
            self.__logger.warning(f"User has no GitHub token")
            return

        # scrape GitHub to synchronize repos and workflow config
        profile = Profile.objects.get(user=user)
        github = GitHubViews(profile.github_token)
        workflows = github.get_connectable_workflows(login)

        removed = 0
        updated = 0
        added = 0

        old_patterns = [key.decode('utf-8') for key in self.__cache.scan_iter(match=f"workflows/{login}/*")]
        new_patterns = [f"workflows/{login}/{wf['repo']['name']}/{wf['branch']['name']}" for wf in workflows]

        for pattern in old_patterns:
            # invalidate submission config cache
            config_key = f"workflow_configs/{user.username}/{pattern.partition('/')[2]}"
            if self.__cache.exists(config_key):
                self.__logger.info(f"Removing user {user.username} (GitHub login {login}) workflow submission configuration: {config_key}")
                self.__cache.delete(config_key)

            # remove old workflow if corresponding repo no longer exists
            if pattern not in new_patterns:
                self.__logger.debug(f"Removing user {user.username} (GitHub login {login}) workflow: {pattern}")
                removed += 1
                self.__cache.delete(pattern)
            # otherwise update workflow
            else:
                self.__logger.debug(f"Updating user {user.username} (GitHub login {login}) workflow: {pattern}")
                updated += 1

        # ...then adding/updating the workflows we just scraped
        for workflow in workflows:
            # set flag if this is a featured workflow
            workflow['featured'] = workflow_is_featured(login, workflow['repo']['name'], workflow['branch']['name'])
            pattern = f"workflows/{login}/{workflow['repo']['name']}/{workflow['branch']['name']}"
            if pattern not in old_patterns:
                self.__logger.debug(f"Adding user {user.username} (GitHub login {login}) workflow: {pattern}")
                added += 1
            self.__cache.set(pattern, json.dumps(del_none(workflow)))

        self.__logger.info(
            f"Updated user {user.username} (GitHub login {login}) workflow cache "
            f"(added {added}, updated {updated}, removed {removed}, now {len(workflows)})")

    def __update_organization_workflow_cache(self, user: User, organization: str):
        login = user.profile.github_username
        token = user.profile.github_token

        if login is None or login == '':
            self.__logger.warning(f"User hasn't linked a GitHub account")
            return

        if token is None or token == '':
            self.__logger.warning(f"User has no GitHub token")
            return

        # scrape GitHub for organization-owned repositories containing workflows
        github = GitHubViews(user.profile.github_token)
        workflows = github.get_connectable_workflows(organization)

        removed = 0
        updated = 0
        added = 0

        old_patterns = [key.decode('utf-8') for key in self.__cache.scan_iter(match=f"workflows/{organization}/*")]
        new_patterns = [f"workflows/{organization}/{wf['repo']['name']}/{wf['branch']['name']}" for wf in workflows]
        for pattern in old_patterns:
            if pattern not in new_patterns:
                self.__logger.debug(f"Removing org workflow {pattern}")
                removed += 1
                self.__cache.delete(pattern)
            else:
                self.__logger.debug(f"Updating user {user.username} (Github login {login}) organization {organization} workflow: {pattern}")
                updated += 1

        # ...then adding/updating the workflows we just scraped
        for workflow in workflows:
            # set flag if this is a featured workflow
            workflow['featured'] = await workflow_is_featured(organization, workflow['repo']['name'], workflow['branch']['name'])

            key = f"workflows/{organization}/{workflow['repo']['name']}/{workflow['branch']['name']}"
            if key not in old_patterns:
                self.__logger.debug(f"Adding org workflow {key}")
                added += 1
            self.__cache.set(key, json.dumps(del_none(workflow)))

        self.__logger.info(
            f"Updated user {user.username} (GitHub login {login}) organization {organization}'s workflow cache "
            f"(added {added}, updated {updated}, removed {removed}, now {len(workflows)})")

    def __get_institutions(self) -> dict:
        # count members per institution
        counts = {i['institution'].lower(): i['institution__count'] for i in statistics.count_institutions()}
        institutions = dict()

        for k in counts.keys():
            # get institution information (TODO: can we send all the requests concurrently?)
            # TODO: need to make sure this doesn't exceed the free plan rate limit
            result = async_to_sync(mapbox.get_institution)(k, settings.MAPBOX_TOKEN)

            # reconstruct institution name with proper capitalization from Mapbox result
            # TODO: are there any edge cases this might fail for?
            name = ' '.join(result['query'])

            # if we can't match the institution name, skip it
            if name not in counts:
                self.__logger.warning(f"Failed to match {name} to any institution")
                continue

            # number of members in this institution
            count = counts[name]

            # if Mapbox returned no results, we can't return geocode information
            if len(result['features']) == 0:
                self.__logger.warning(f"No results from Mapbox for institution: {name}")
                institutions[name] = {
                    'institution': name,
                    'count': count,
                    'geocode': None
                }

            # if we got results, pick the top one
            else:
                feature = result['features'][0]
                feature['id'] = name
                feature['properties'] = {
                    'name': name,
                    'count': count
                }
                institutions[name] = {
                    'institution': name,
                    'count': count,
                    'geocode': feature
                }

        return institutions

    def __get_total_counts(self) -> dict:
        workflows = [json.loads(self.__cache.get(key)) for key in self.__cache.scan_iter('workflows/*')]
        developers = list(set([wf['repo']['owner']['login'] for wf in workflows]))
        completion_states = [TaskStatus.COMPLETED, TaskStatus.FAILURE, TaskStatus.TIMEOUT, TaskStatus.CANCELED]

        return {
            'users': User.objects.count(),
            'online': len(filter_online_users(User.objects.all())),  # TODO store this in the DB each time the user logs in,
            'workflows': len(workflows),
            'developers': len(developers),
            'agents': Agent.objects.count(),
            'tasks': TaskCounter.load().count,
            'running': len(list(Task.objects.exclude(status__in=completion_states))),
            'institutions': len(self.get_institutions().keys())
        }

    def __get_aggregate_timeseries(self):
        return {
            'users_total': [(user.profile.created.isoformat(), i + 1) for i, user in enumerate(User.objects.all().order_by('profile__created'))],
            'tasks_total': [(task['created'].isoformat(), i + 1) for i, task in enumerate(Task.objects.all().values('created').order_by('created'))],
            'tasks_usage': statistics.get_tasks_usage_timeseries(),
            'agents_usage': statistics.get_agents_usage_timeseries(),
            'workflows_usage': statistics.get_workflows_usage_timeseries(),
        }

    def __get_user_timeseries(self, user: User) -> dict:
        return {
            'tasks_usage': statistics.get_tasks_usage_timeseries(user=user),
            'agents_usage': statistics.get_agents_usage_timeseries(user),
            'workflows_usage': statistics.get_workflows_usage_timeseries(user)
        }

    def __get_user_statistics(self, user: User):
        tasks_all = self.get_tasks(user=user)
        tasks_completed = self.get_tasks(user=user, completed=True)
        workflows_used = [f"{task.workflow_owner}/{task.workflow_name}" for task in tasks_all]
        workflows_used_counter = Counter(workflows_used)
        workflows_used_unique = list(np.unique(workflows_used))
        agents_used = [(agent_to_dict(agent, user.username))['name'] for agent in
                       [a for a in [task.agent for task in tasks_all] if a is not None]]
        agents_used_counter = Counter(agents_used)
        agents_used_unique = list(np.unique(agents_used))
        projects_used = [(project_to_dict(project)) for project in
                         [p for p in [task.project for task in tasks_all] if p is not None]]
        projects_used_counter = Counter([f"{project['guid']} ({project['title']})" for project in projects_used])

        return {
            'total_tasks': len(tasks_all),
            'total_task_seconds': sum([(task.completed - task.created).total_seconds() for task in tasks_completed]),
            'owned_workflows': [
                f"{workflow['repo']['owner']['login']}/{workflow['name'] if 'name' in workflow else '[unnamed]'}"
                for workflow in self.get_user_workflows(user=user)],
            'workflow_usage': {
                'values': [workflows_used_counter[workflow] for workflow in workflows_used_unique],
                'labels': workflows_used_unique,
            },
            'agent_usage': {
                'values': [agents_used_counter[agent] for agent in agents_used_unique],
                'labels': agents_used_unique,
            },
            'project_usage': {
                'values': list(dict(projects_used_counter).values()),
                'labels': list(dict(projects_used_counter).keys()),
            },
            'task_status': {
                'values': [1 if task.status == 'success' else 0 for task in tasks_all],
                'labels': ['SUCCESS' if task.status == 'success' else 'FAILURE' for task in tasks_all],
            },
            'owned_agents': [(agent_to_dict(agent, user.username))['name'] for agent in
                             [agent for agent in self.get_agents(user=user) if agent is not None]],
            'guest_agents': [(agent_to_dict(agent, user.username))['name'] for agent in
                             [agent for agent in self.get_agents(user=user) if agent is not None]],
            'institution': Profile.objects.get(user=user).institution,
            'tasks_running': statistics.get_tasks_usage_timeseries(user=user)
        }

    def __get_workflow_usage_timeseries(self, owner: str, repo: str, branch: str):
        series = dict()
        tasks = Task.objects.filter(
            workflow__repo__owner=owner,
            workflow__repo__name=repo,
            workflow__repo__branch=branch)

        if len(tasks) == 0:
            return series

        # count tasks per workflow
        for task in tasks:
            timestamp = datetime.combine(task.created.date(), datetime.min.time()).isoformat()
            if timestamp not in series: series[timestamp] = 0
            series[timestamp] = series[timestamp] + 1

        return series
