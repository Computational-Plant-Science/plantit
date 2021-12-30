import json

from django.contrib.auth.models import User
from django.http import JsonResponse

from plantit.tasks.models import Task, TaskCounter, TaskStatus
from plantit.utils import list_institutions, filter_online, get_tasks_running_timeseries
from plantit.redis import RedisClient


def counts(request):
    # count users online by checking their CyVerse token expiry times
    users = list(User.objects.all())
    online = filter_online(users)
    redis = RedisClient.get()
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
    users_x = []
    users_y = []
    for i, user in enumerate(User.objects.all().order_by('profile__created')):
        users_x.append(user.profile.created)
        users_y.append(i + 1)

    tasks_x = []
    tasks_y = []
    for i, task in enumerate(Task.objects.all().order_by('created')):
        tasks_x.append(task.created)
        tasks_y.append(i + 1)

    redis = RedisClient.get()
    tasks_running = redis.get('tasks_running')
    if tasks_running is not None: tasks_running = json.loads(tasks_running)
    else: tasks_running = dict()
    tasks_running_x = list(tasks_running.keys())
    tasks_running_y = list(tasks_running.values())

    return JsonResponse({
        'users': {
            'x': users_x,
            'y': users_y,
            'type': 'scatter'
        },
        'tasks': {
            'x': tasks_x,
            'y': tasks_y,
            'type': 'scatter'
        },
        'tasks_running': {
            'x': tasks_running_x,
            'y': tasks_running_y,
            'type': 'scatter'
        }
    })
