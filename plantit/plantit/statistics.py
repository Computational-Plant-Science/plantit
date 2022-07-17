import json
from collections import OrderedDict, Counter
from datetime import datetime, timedelta
from typing import List, Tuple

import numpy as np
import pandas as pd
from asgiref.sync import async_to_sync
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils import timezone

from plantit import mapbox as mapbox, loess as loess
from plantit.agents.models import Agent
from plantit.workflows import logger, list_user_workflows
from plantit.filters import filter_tasks, filter_agents, filter_online_users
from plantit.redis import RedisClient
from plantit.serialize import agent_to_dict, project_to_dict
from plantit.tasks.models import TaskCounter, Task, TaskStatus
from plantit.users.models import Profile


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

            # if we can't match the institution name, skip it
            if name not in counts:
                logger.warning(f"Failed to match {name} to any institution")
                continue

            # number of members in this institution
            count = counts[name]

            # if Mapbox returned no results, we can't return geocode information
            if len(result['features']) == 0:
                logger.warning(f"No results from Mapbox for institution: {name}")
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
        online = len(filter_online_users(User.objects.all()))  # TODO store this in the DB each time the user logs in
        wfs = [json.loads(redis.get(key)) for key in redis.scan_iter('workflows/*')]
        devs = list(set([wf['repo']['owner']['login'] for wf in wfs]))
        workflows = len(wfs)
        developers = len(devs)
        agents = Agent.objects.count()
        tasks = TaskCounter.load().count
        running = len(list(Task.objects.exclude(status__in=[TaskStatus.COMPLETED, TaskStatus.FAILURE, TaskStatus.TIMEOUT, TaskStatus.CANCELED])))
        institutions = len(get_institutions().keys())
        counts = {
            'users': users,
            'online': online,
            'workflows': workflows,
            'developers': developers,
            'agents': agents,
            'tasks': tasks,
            'running': running,
            'institutions': institutions
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


def get_user_statistics(user: User, invalidate: bool = False) -> dict:
    redis = RedisClient.get()
    cached = redis.get(f"stats/{user.username}")

    if cached is None or invalidate:
        profile = Profile.objects.get(user=user)
        all_tasks = filter_tasks(user=user)
        completed_tasks = filter_tasks(user=user, completed=True)
        total_tasks = len(all_tasks)
        total_time = sum([(task.completed - task.created).total_seconds() for task in completed_tasks])
        owned_workflows = [
            f"{workflow['repo']['owner']['login']}/{workflow['name'] if 'name' in workflow else '[unnamed]'}"
            for
            workflow in list_user_workflows(owner=profile.github_username)] if profile.github_username != '' else []
        used_workflows = [f"{task.workflow_owner}/{task.workflow_name}" for task in all_tasks]
        used_workflows_counter = Counter(used_workflows)
        unique_used_workflows = list(np.unique(used_workflows))
        owned_agents = [(agent_to_dict(agent, user.username))['name'] for agent in
                        [agent for agent in filter_agents(user=user) if agent is not None]]
        guest_agents = [(agent_to_dict(agent, user.username))['name'] for agent in
                        [agent for agent in filter_agents(user=user) if agent is not None]]
        used_agents = [(agent_to_dict(agent, user.username))['name'] for agent in
                       [a for a in [task.agent for task in all_tasks] if a is not None]]
        used_projects = [(project_to_dict(project)) for project in
                         [p for p in [task.project for task in all_tasks] if p is not None]]
        used_agents_counter = Counter(used_agents)
        used_projects_counter = Counter([f"{project['guid']} ({project['title']})" for project in used_projects])
        unique_used_agents = list(np.unique(used_agents))
        tasks_running = get_tasks_usage_timeseries(600, user)

        stats = {
            'total_tasks': total_tasks,
            'total_task_seconds': total_time,
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
        redis.set(f"stats/{user.username}", json.dumps(stats))
    else:
        stats = json.loads(cached)
    return stats
