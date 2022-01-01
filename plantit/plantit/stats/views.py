import json

from django.contrib.auth.models import User
from django.http import JsonResponse

from plantit.tasks.models import Task, TaskCounter, TaskStatus
from plantit.utils import list_institutions, filter_online, get_users_timeseries, get_tasks_timeseries, get_tasks_running_timeseries
from plantit.redis import RedisClient


def counts(request):
    redis = RedisClient.get()

    # count users online by checking their CyVerse token expiry times
    users = list(User.objects.all())
    online = filter_online(users)
    workflows = len(list(redis.scan_iter('workflows/*')))

    return JsonResponse({
        'users': len(users),
        'online': len(online),
        'workflows': workflows,
        'tasks': TaskCounter.load().count,
        'running': len(list(Task.objects.exclude(status__in=[TaskStatus.SUCCESS, TaskStatus.FAILURE, TaskStatus.TIMEOUT, TaskStatus.CANCELED])))
    })


def institutions(request):
    return JsonResponse({'institutions': list_institutions()})


def timeseries(request):
    redis = RedisClient.get()
    cached_users = redis.get('users_timeseries')
    cached_tasks = redis.get('tasks_timeseries')
    cached_running = redis.get('tasks_running')

    users = json.loads(cached_users) if cached_users is not None else get_users_timeseries()
    tasks = json.loads(cached_tasks) if cached_tasks is not None else get_tasks_timeseries()
    tasks_running = json.loads(cached_running) if cached_running is not None else get_tasks_running_timeseries()

    return JsonResponse({
        'users': {
            'x': [u[0] for u in users],
            'y': [u[1] for u in users],
            'type': 'scatter'
        },
        'tasks': {
            'x': [t[0] for t in tasks],
            'y': [t[1] for t in tasks],
            'type': 'scatter'
        },
        'tasks_running': {
            'x': list(tasks_running.keys()),
            'y': list(tasks_running.values()),
            'type': 'scatter'
        }
    })
