import json
import logging
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
from plantit.filters import filter_tasks, filter_agents, filter_online_users
from plantit.redis import RedisClient
from plantit.serialize import agent_to_dict, project_to_dict
from plantit.tasks.models import TaskCounter, Task, TaskStatus
from plantit.users.models import Profile

logger = logging.getLogger(__name__)


def count_institutions() -> list:
    return list(Profile.objects.exclude(institution__exact='').values('institution').annotate(Count('institution')))


def get_tasks_usage_timeseries(user: User = None, interval_seconds: int = 600) -> dict:
    series = dict()
    tasks = Task.objects.all() if user is None \
        else Task.objects.filter(user=user).order_by('-completed')[:100]  # TODO make limit configurable

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


def get_workflows_usage_timeseries(user: User = None) -> dict:
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


def get_agents_usage_timeseries(user: User = None) -> dict:
    series = dict()
    tasks = Task.objects.filter(agent__public=True).order_by('-created') if user is None \
        else Task.objects.filter(user=user).order_by('-created')[:100]  # TODO: make limit configurable

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
