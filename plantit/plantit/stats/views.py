from django.contrib.auth.models import User
from django.http import JsonResponse

from plantit.tasks.models import Task, TaskCounter, TaskStatus
from plantit.utils import list_institutions, filter_online
from plantit.workflows.models import Workflow


def counts(request):
    # count users online by checking their CyVerse token expiry times
    users = list(User.objects.all())
    online = filter_online(users)

    return JsonResponse({
        'users': len(users),
        'online': len(online),
        'workflows': Workflow.objects.count(),
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
        }
    })
