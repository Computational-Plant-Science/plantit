from django.contrib.auth.models import User
from django.db.models import Count
from django.http import JsonResponse

import jwt
from datetime import datetime, timezone

from plantit.tasks.models import Task, TaskCounter
from plantit.users.models import Profile
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
        'tasks': TaskCounter.load().count
    })


def institutions(request):
    return JsonResponse({'institutions': list_institutions()})
