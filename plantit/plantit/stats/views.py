import json

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from plantit.agents.models import Agent
from plantit.tasks.models import Task, TaskCounter, TaskStatus
from plantit.utils import list_institutions, filter_online, get_total_counts get_user_timeseries, get_users_total_timeseries, get_tasks_total_timeseries, get_tasks_usage_timeseries, get_workflow_usage_timeseries, get_workflows_usage_timeseries, get_agents_usage_timeseries, get_stats_counts
from plantit.redis import RedisClient


def institutions_info(_):
    redis = RedisClient.get()
    cached = list(redis.scan_iter(match=f"institutions/*"))

    if len(cached) != 0:
        institutions = [json.loads(redis.get(key)) for key in cached]
    else:
        institutions = list_institutions()
        for i in institutions: redis.set(f"institutions/{i['name']}", json.dumps(i))

    return JsonResponse(institutions)


def total_counts(_):
    redis = RedisClient.get()
    cached = redis.get("stats_counts")

    if cached is not None:
        counts = json.loads(cached)
    else:
        counts = get_total_counts()
        redis.set("stats_counts", counts)

    return JsonResponse(counts)


def total_timeseries(_):
    redis = RedisClient.get()
    cached = redis.get("total_timeseries")

    if cached is not None:
        series = json.loads(cached)
    else:
        series = get_total_timeseries()
        redis.set("total_timeseries", series)

    return JsonResponse(series)


@login_required
def workflow_timeseries(_, owner, name, branch):
    redis = RedisClient.get()
    cached = redis.get(f"workflow_timeseries/{owner}/{name}/{branch}")

    if cached is not None:
        series = json.loads(cached)
    else:
        series = get_workflow_timeseries(owner, name, branch)
        redis.set(f"workflow_timeseries/{owner}/{name}/{branch}", json.dumps(series))

    return JsonResponse(series)


@login_required
def user_timeseries(request):
    redis = RedisClient.get()
    cached_user_running = redis.get(f"user_tasks_running/{request.user.username}")
    cached_user_workflows_running = redis.get(f"workflows_running/{request.user.username}")
    cached_user_agents_running = redis.get(f"agents_running/{request.user.username}")

    cached = redis.get(f"user_timeseries/{request.user.username}")
    if cached is not None:
        series = json.loads(cached)
    else:
        series = get_user_timeseries(request.user)

    return JsonResponse({
        'user_tasks_running': {
            'x': list(user_tasks_running.keys()),
            'y': list(user_tasks_running.values()),
            'type': 'scatter'
        },
        'user_workflows_running': {k: {
            'x': list([kk for kk in v.keys()]),
            'y': list([vv for vv in v.values()]),
            'type': 'scatter'
        } for k, v in user_workflows_running.items()},
        'user_agents_running': {k: {
            'x': list([kk for kk in v.keys()]),
            'y': list([vv for vv in v.values()]),
            'type': 'scatter'
        } for k, v in user_agents_running.items()},
    })
