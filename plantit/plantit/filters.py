from datetime import datetime
from typing import Optional, List, Dict

import jwt
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.utils import timezone

from plantit.agents.models import Agent
from plantit.miappe.models import Investigation
from plantit.misc.models import FeaturedWorkflow
from plantit.notifications.models import Notification
from plantit.serialize import notification_to_dict, task_to_dict, delayed_task_to_dict, repeating_task_to_dict, triggered_task_to_dict, \
    project_to_dict
from plantit.tasks.models import Task, DelayedTask, RepeatingTask, TriggeredTask
from plantit.users.models import ManagedFile
from plantit.cache import list_project_workflows, list_org_workflows
from plantit.github import get_member_organizations


def filter_notifications(user: User, page: int = 1, read: Optional[bool] = None):
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
        'notifications': [notification_to_dict(notification) for notification in list(paged)]
    }


def filter_tasks(user: User, completed: bool = None):
    tasks = Task.objects.filter(user=user, completed__isnull=False) if completed else Task.objects.filter(user=user)
    return list(tasks)


def filter_tasks_paged(user: User, page: int = 1, completed: Optional[bool] = None):
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
        'tasks': [task_to_dict(task) for task in list(paged)]
    }


def filter_delayed_tasks(user: User):
    # TODO: paginate
    return [delayed_task_to_dict(task) for task in DelayedTask.objects.filter(user=user, enabled=True)]


def filter_repeating_tasks(user: User):
    # TODO: paginate
    return [repeating_task_to_dict(task) for task in RepeatingTask.objects.filter(user=user, enabled=True)]


def filter_triggered_tasks(user: User):
    return [triggered_task_to_dict(task) for task in TriggeredTask.objects.filter(user=user, enabled=True)]


def filter_agents(user: User):
    # only return public agents and agents the requesting user is authorized to access
    return [agent for agent in Agent.objects.all() if
            agent.user == user or
            agent.public
            or user.username in [u.username for u in agent.users_authorized.all()]]


def filter_online_users(users: List[User]) -> List[User]:
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


def filter_managed_files(user: User, page: int = 1):
    files = ManagedFile.objects.filter(user=user)
    paginator = Paginator(files, 20)
    paged = paginator.get_page(page)
    return {
        'previous_page': paged.has_previous() and paged.previous_page_number() or None,
        'next_page': paged.has_next() and paged.next_page_number() or None,
        'files': [task_to_dict(file) for file in list(paged)]
    }


def filter_user_projects(user: User):
    return list(Investigation.objects.filter(owner=user)) + list(user.project_teams.all())


def filter_team_projects(team=None):
    return [project_to_dict(project) for project in (Investigation.objects.all() if team is None else Investigation.objects.filter(team__username=team))]


def workflow_is_featured(owner, name, branch):
    return FeaturedWorkflow.objects.filter(owner=owner, name=name, branch=branch).exists()


def list_user_project_workflows(user: User) -> Dict[str, List[dict]]:
    projects = filter_user_projects(user)
    return {project.guid: list_project_workflows(project) for project in projects}


def list_user_org_workflows(user: User) -> Dict[str, List[dict]]:
    orgs = get_member_organizations(user)
    workflows = dict()
    for org in orgs: workflows[org['login']] = list_org_workflows(org['login'])
    return workflows
