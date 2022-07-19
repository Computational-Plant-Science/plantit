import json
import logging
from abc import ABCMeta, abstractmethod
from collections import Counter, OrderedDict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

import jwt
import numpy as np
import pandas as pd
from asgiref.sync import async_to_sync
from django.conf import settings
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone
from redis import Redis

import plantit.loess as loess
import plantit.mapbox as mapbox
from plantit.agents.models import Agent, AgentRole
from plantit.datasets.models import DatasetAccessPolicy
from plantit.github import GitHubViews
from plantit.health import is_healthy
from plantit.miappe.models import Investigation, Study
from plantit.misc.models import NewsUpdate, FeaturedWorkflow
from plantit.notifications.models import Notification
from plantit.tasks.models import TaskCounter, Task, TaskStatus, DelayedTask, RepeatingTask, TriggeredTask
from plantit.users.models import Profile, ManagedFile, Migration
from plantit.utils.misc import del_none
from plantit.utils.tasks import has_output_target, get_task_orchestrator_log_file_path


class ManualCacheViews(metaclass=ABCMeta):
    @abstractmethod
    def get_users(self, invalidate: bool = False):
        pass

    @abstractmethod
    def get_user_workflow(self,
                          user: User,
                          owner: str,
                          repo: str,
                          branch: str,
                          invalidate: bool = False) -> dict:
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
    def get_workflows(self, invalidate=True):
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

    @abstractmethod
    def get_agent_healthchecks(self, invalidate: bool = False) -> List[dict]:
        pass


class CacheopsViews(metaclass=ABCMeta):
    @abstractmethod
    def get_agents(self, user: User) -> List[Agent]:
        pass

    @abstractmethod
    def get_online_users(self) -> List[User]:
        pass

    @abstractmethod
    def get_managed_files_paged(self, user: User, page: int = 1) -> dict:
        pass

    @abstractmethod
    def get_user_projects(self, user: User) -> List[Investigation]:
        pass

    @abstractmethod
    def get_team_projects(self, member: str) -> List[Investigation]:
        pass

    @abstractmethod
    def get_tasks(self, user: User, completed: bool = None) -> List[Task]:
        pass

    @abstractmethod
    def get_tasks_paged(self, user: User, page: int = 1, completed: Optional[bool] = None) -> dict:
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

    @abstractmethod
    def get_notifications_paged(self, user: User, page: int = 1, read: Optional[bool] = None) -> dict:
        pass


class ModelViews(ManualCacheViews, CacheopsViews):
    def __init__(self, cache: Redis):
        super(ModelViews, self).__init__()

        if cache is None:
            raise ValueError(f"Redis client must be provided")

        self.__logger = logging.getLogger(ModelViews.__name__)
        self.__cache = cache

    # manual cache views

    def get_users(self, invalidate: bool = False):
        pattern = "users/*"
        matches = list(self.__cache.scan_iter(match=pattern))

        if len(matches) == 0 or invalidate:
            self.__logger.info(f"Refreshing user cache")
            users = self.__get_users()
            for user in users:
                self.__cache.set(f"users/{user.username}", json.dumps(user))

        return [json.loads(self.__cache.get(match)) for match in matches]

    def get_user_workflow(self,
                          user: User,
                          login: str,
                          repo: str,
                          branch: str,
                          invalidate: bool = False) -> dict:
        pattern = f"workflows/{login}/{repo}/{branch}"
        workflow = self.__cache.get(pattern)

        if workflow is None or invalidate:
            github = GitHubViews(user.profile.github_token)
            workflow = github.get_workflow_bundle(login, repo, branch)
            self.__cache.set(pattern, json.dumps(del_none(workflow)))
            return workflow
        else:
            return json.loads(workflow)

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
        projects = self.get_user_projects(user)
        return {project.guid: self.get_project_workflows(project) for project in projects}

    def get_user_org_workflows(self, user: User) -> Dict[str, List[dict]]:
        organizations = GitHubViews.get_member_organizations(user)
        workflows = dict()
        for org in organizations: workflows[org['login']] = self.get_organization_workflows(user, org['login'])
        return workflows

    def get_workflows(self, invalidate=True):
        workflows = []
        # refresh workflows from repos owned by logged-in users
        online = self.get_online_users()
        self.__logger.info(f"Refreshing workflow cache for {len(online)} user(s)")
        for user in online:
            profile = Profile.objects.get(user=user)
            github_login = profile.github_username
            if github_login is not None and github_login != '':
                workflows = workflows + self.get_user_workflows(user, invalidate=invalidate)

        # refresh workflows belonging to user organizations
        for user in online:
            organizations = GitHubViews.get_member_organizations(user)
            self.__logger.info(f"Refreshing workflow cache for user {user.username}'s {len(online)} organizations")
            for org in organizations:
                workflows = workflows + self.get_organization_workflows(user, organization=org['login'], invalidate=invalidate)

        return workflows

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
            series = ModelViews.__get_aggregate_timeseries()
            self.__cache.set(pattern, json.dumps(series))
        else:
            series = json.loads(cached)

        return series

    def get_user_timeseries(self, user: User, invalidate: bool = False) -> dict:
        pattern = f"user_timeseries/{user.username}"
        cached = self.__cache.get(pattern)

        if cached is None or invalidate:
            series = ModelViews.__get_user_timeseries(user)
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
            series = ModelViews.__get_workflow_usage_timeseries(owner=owner, repo=repo, branch=branch)
            self.__cache.set(pattern, json.dumps(series))
        else:
            series = json.loads(cached)

        return series

    def get_agent_healthchecks(self, invalidate=True) -> List[dict]:
        checks = []
        for agent in Agent.objects.all():
            pattern = f"healthchecks/{agent.name}"
            cached = [json.loads(self.__cache.get(key)) for key in self.__cache.scan_iter(match=pattern)]

            if len(cached) == 0 or invalidate:
                # check and persist agent's health
                healthy, output = is_healthy(agent)
                agent.is_healthy = healthy
                agent.save()

                # save healthcheck to cache
                length = self.__cache.llen(pattern)
                checks_saved = int(settings.AGENTS_HEALTHCHECKS_SAVED)
                if length > checks_saved: self.__cache.rpop(pattern)
                check = {
                    'agent': agent.name,
                    'timestamp': timezone.now().isoformat(),
                    'healthy': healthy,
                    'output': output
                }
                checks.append(check)
                self.__cache.lpush(pattern, json.dumps(check))

        return checks

    # automatic (cacheops) views

    def get_agents(self, user: User) -> List[Agent]:
        # only return public agents and agents the requesting user is authorized to access
        return [agent for agent in Agent.objects.all() if
                agent.user == user or
                agent.public
                or user.username in [u.username for u in agent.users_authorized.all()]]

    def get_online_users(self) -> List[User]:
        """
        Selects only those users currently online by checking their Terrain token expiry times

        :param users: The list of users
        :return: The logged-in users
        """

        def is_expired(token):
            decoded = jwt.decode(token, options={
                'verify_signature': False,
                'verify_aud': False,
                'verify_iat': False,
                'verify_exp': False,
                'verify_iss': False
            })
            exp = datetime.fromtimestamp(decoded['exp'], timezone.utc)
            now = datetime.now(tz=timezone.utc)

            if now > exp:
                self.__logger.warning(f"Session for {decoded['preferred_username']} expired at {exp.isoformat()}")
                return True
            else:
                self.__logger.info(f"Session for {decoded['preferred_username']} valid until {exp.isoformat()}")
                return False

        return [user for user in User.objects.all() if is_expired(user.profile.cyverse_access_token)]

    def get_managed_files_paged(self, user: User, page: int = 1) -> dict:
        files = ManagedFile.objects.filter(user=user)
        paginator = Paginator(files, 20)
        paged = paginator.get_page(page)

        return {
            'previous_page': paged.has_previous() and paged.previous_page_number() or None,
            'next_page': paged.has_next() and paged.next_page_number() or None,
            'files': [self.task_to_dict(file) for file in list(paged)]
        }

    def get_user_projects(self, user: User) -> List[Investigation]:
        return list(Investigation.objects.filter(owner=user)) + list(user.project_teams.all())

    def get_team_projects(self, member: str) -> List[Investigation]:
        if member is None or member == '':
            raise ValueError(f"Team member username must be provided")

        return Investigation.objects.filter(team__username=member)

    def get_tasks(self, user: User, completed: bool = None) -> List[Task]:
        return list(Task.objects.filter(user=user, completed__isnull=False) if completed else Task.objects.filter(user=user))

    def get_tasks_paged(self, user: User, page: int = 1, completed: Optional[bool] = None) -> dict:
        if completed is None:
            tasks = Task.objects.filter(user=user)
        elif not completed:
            tasks = Task.objects.filter(user=user, completed__isnull=True)
        else:
            tasks = Task.objects.filter(user=user, completed__isnull=False)

        # TODO configure default page size from settings
        paginator = Paginator(tasks, 20)
        paged = paginator.get_page(page)
        return {
            'previous_page': paged.has_previous() and paged.previous_page_number() or None,
            'next_page': paged.has_next() and paged.next_page_number() or None,
            'tasks': [self.task_to_dict(task) for task in list(paged)]
        }

    def get_delayed_tasks(self, user: User) -> List[DelayedTask]:
        # TODO: paginate
        return DelayedTask.objects.filter(user=user, enabled=True)

    def get_repeating_tasks(self, user: User) -> List[RepeatingTask]:
        # TODO: paginate
        return RepeatingTask.objects.filter(user=user, enabled=True)

    def get_triggered_tasks(self, user: User) -> List[TriggeredTask]:
        # TODO: paginate
        return TriggeredTask.objects.filter(user=user, enabled=True)

    def workflow_is_featured(self, owner: str, name: str, branch: str) -> bool:
        return FeaturedWorkflow.objects.filter(owner=owner, name=name, branch=branch).exists()

    def get_notifications_paged(self, user: User, page: int = 1, read: Optional[bool] = None):
        if read is None:
            notifications = Notification.objects.filter(user=user)
        else:
            notifications = Notification.objects.filter(user=user, read__exact=read)

        # TODO configure default page size from settings
        paginator = Paginator(notifications, 20)
        paged = paginator.get_page(page)
        return {
            'previous_page': paged.has_previous() and paged.previous_page_number() or None,
            'next_page': paged.has_next() and paged.next_page_number() or None,
            'notifications': [ModelViews.notification_to_dict(notification) for notification in list(paged)]
        }

    # internal update methods

    def __get_user_bundle(self, user: User):
        profile = Profile.objects.get(user=user)
        github = GitHubViews(profile.github_token)
        if not github.has_github_profile(profile):
            return {
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        else:
            cached = self.__cache.get(f"users/{user.username}")
            if cached is not None: return json.loads(cached)
            github_profile = async_to_sync(github.get_profile)(profile.github_username)
            github_organizations = async_to_sync(GitHubViews.get_member_organizations)(user)
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
            self.__cache.set(f"users/{user.username}", json.dumps(bundle))
            return bundle

    def __get_users(self):
        users = [self.__get_user_bundle(user) for user in list(User.objects.all().exclude(profile__isnull=True))]
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
            workflow['featured'] = self.workflow_is_featured(login, workflow['repo']['name'], workflow['branch']['name'])
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
            workflow['featured'] = self.workflow_is_featured(organization, workflow['repo']['name'], workflow['branch']['name'])

            key = f"workflows/{organization}/{workflow['repo']['name']}/{workflow['branch']['name']}"
            if key not in old_patterns:
                self.__logger.debug(f"Adding org workflow {key}")
                added += 1
            self.__cache.set(key, json.dumps(del_none(workflow)))

        self.__logger.info(
            f"Updated user {user.username} (GitHub login {login}) organization {organization}'s workflow cache "
            f"(added {added}, updated {updated}, removed {removed}, now {len(workflows)})")

    @staticmethod
    def __count_institutions() -> list:
        return list(Profile.objects.exclude(institution__exact='').values('institution').annotate(Count('institution')))

    def __get_institutions(self) -> dict:
        # count members per institution
        counts = {i['institution'].lower(): i['institution__count'] for i in ModelViews.__count_institutions()}
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
            'online': len(self.get_online_users()),  # TODO store this in the DB each time the user logs in,
            'workflows': len(workflows),
            'developers': len(developers),
            'agents': Agent.objects.count(),
            'tasks': TaskCounter.load().count,
            'running': len(list(Task.objects.exclude(status__in=completion_states))),
            'institutions': len(self.get_institutions().keys())
        }

    @staticmethod
    def __get_aggregate_timeseries():
        return {
            'users_total': [(user.profile.created.isoformat(), i + 1) for i, user in enumerate(User.objects.all().order_by('profile__created'))],
            'tasks_total': [(task['created'].isoformat(), i + 1) for i, task in enumerate(Task.objects.all().values('created').order_by('created'))],
            'tasks_usage': ModelViews.__get_tasks_usage_timeseries(),
            'agents_usage': ModelViews.__get_agents_usage_timeseries(),
            'workflows_usage': ModelViews.__get_workflows_usage_timeseries(),
        }

    @staticmethod
    def __get_user_timeseries(user: User) -> dict:
        return {
            'tasks_usage': ModelViews.__get_tasks_usage_timeseries(user=user),
            'agents_usage': ModelViews.__get_agents_usage_timeseries(user),
            'workflows_usage': ModelViews.__get_workflows_usage_timeseries(user)
        }

    def __get_user_statistics(self, user: User):
        tasks_all = self.get_tasks(user=user)
        tasks_completed = self.get_tasks(user=user, completed=True)
        workflows_used = [f"{task.workflow_owner}/{task.workflow_name}" for task in tasks_all]
        workflows_used_counter = Counter(workflows_used)
        workflows_used_unique = list(np.unique(workflows_used))
        agents_used = [(ModelViews.agent_to_dict(agent, user.username))['name'] for agent in
                       [a for a in [task.agent for task in tasks_all] if a is not None]]
        agents_used_counter = Counter(agents_used)
        agents_used_unique = list(np.unique(agents_used))
        projects_used = [(ModelViews.project_to_dict(project)) for project in
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
            'owned_agents': [(ModelViews.agent_to_dict(agent, user.username))['name'] for agent in
                             [agent for agent in self.get_agents(user=user) if agent is not None]],
            'guest_agents': [(ModelViews.agent_to_dict(agent, user.username))['name'] for agent in
                             [agent for agent in self.get_agents(user=user) if agent is not None]],
            'institution': Profile.objects.get(user=user).institution,
            'tasks_running': ModelViews.__get_tasks_usage_timeseries(user=user)
        }

    @staticmethod
    def __get_workflow_usage_timeseries(owner: str, repo: str, branch: str):
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

    @staticmethod
    def __get_workflows_usage_timeseries(user: User = None) -> dict:
        # get stats moving window width from settings
        window_width_days = int(settings.STATS_WINDOW_WIDTH_DAYS)

        # starting date of window
        start = timezone.now().date() - timedelta(days=window_width_days)

        # if a user is provided, filter only tasks owned by that user, otherwise public tasks
        tasks = Task.objects.filter(workflow__public=True, created__gte=start) if user is None \
            else Task.objects.filter(user=user, created__gte=start)
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

    @staticmethod
    def __get_tasks_usage_timeseries(user: User = None, interval_seconds: int = 600) -> dict:
        series = dict()
        tasks = Task.objects.all() if user is None \
            else Task.objects.filter(user=user).order_by('-completed')[:100]  # TODO make limit configurable

        if len(tasks) == 0:
            return series

        # find running interval for each task
        start_end_times = dict()
        for task in tasks:
            start_end_times[task.guid] = (task.created, task.completed if task.completed is not None else timezone.now())

        # count running tasks for each value in the time domain
        start = min([v[0] for v in start_end_times.values()])
        end = max(v[1] for v in start_end_times.values())
        for t in range(int(start.timestamp()), int(end.timestamp()), interval_seconds):
            running = len([1 for k, se in start_end_times.items() if int(se[0].timestamp()) <= t <= int(se[1].timestamp())])
            series[t] = running

        # smooth timeseries with LOESS regression
        series_keys = list(series.keys())
        series_frame = pd.DataFrame({'X': series_keys, 'Y': list(series.values())})
        smoothed_frame = loess.regress(series_frame, bandwidth=int(interval_seconds / 5), num_pts=int(len(series_keys) / 2))

        return {datetime.fromtimestamp(row['X']).isoformat(): row['Y'] for i, row in smoothed_frame.iterrows()}

    @staticmethod
    def get_agent_usage_timeseries(agent: Agent) -> dict:
        series = dict()
        tasks = Task.objects.filter(agent=agent).order_by('-created')

        if len(tasks) == 0:
            return series

        # count tasks per agent
        for task in tasks:
            timestamp = datetime.combine(task.created.date(), datetime.min.time()).isoformat()
            if timestamp not in series: series[timestamp] = 0
            series[timestamp] = series[timestamp] + 1

        return series

    @staticmethod
    def __get_agents_usage_timeseries(user: User = None) -> dict:
        series = dict()
        tasks = Task.objects.filter(agent__public=True).order_by('-created') if user is None \
            else Task.objects.filter(user=user).order_by('-created')[:100]  # TODO: make limit configurable

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

    # serialization methods

    @staticmethod
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

    @staticmethod
    def dataset_access_policy_to_dict(policy: DatasetAccessPolicy):
        return {
            'owner': policy.owner.username,
            'guest': policy.guest.username,
            'path': policy.path,
            'role': policy.role.value
        }

    def task_to_dict(self, task: Task) -> dict:
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

        pattern = f"results/{task.guid}"
        results = self.__cache.get(pattern)

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
            'agent': ModelViews.agent_to_dict(task.agent) if task.agent is not None else None,
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def study_to_dict(study: Study, project: Investigation) -> dict:
        team = [ModelViews.person_to_dict(person, 'Researcher') for person in study.team.all()]
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

    @staticmethod
    def project_to_dict(project: Investigation) -> dict:
        studies = [ModelViews.study_to_dict(study, project) for study in Study.objects.select_related().filter(investigation=project)]
        team = [ModelViews.person_to_dict(person, 'Researcher') for person in project.team.all()]
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

    @staticmethod
    def notification_to_dict(notification: Notification) -> dict:
        return {
            'id': notification.guid,
            'username': notification.user.username,
            'created': notification.created.isoformat(),
            'message': notification.message,
            'read': notification.read,
        }

    @staticmethod
    def person_to_dict(user: User, role: str) -> dict:
        return {
            'name': f"{user.first_name} {user.last_name}",
            'email': user.email,
            'username': user.username,
            'affiliation': user.profile.institution,
            'role': role,
        }

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def update_to_dict(update: NewsUpdate):
        return {
            'created': update.created.isoformat(),
            'content': update.content
        }
