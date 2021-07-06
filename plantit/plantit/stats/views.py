from django.contrib.auth.models import User
from django.db.models import Count
from django.http import JsonResponse

from plantit.tasks.models import Task, TaskCounter
from plantit.users.models import Profile
from plantit.utils import list_institutions
from plantit.workflows.models import Workflow


def counts(request):
    return JsonResponse({
        'users': User.objects.count(),
        'workflows': Workflow.objects.count(),
        'tasks': TaskCounter.load().count
    })


def institutions(request):
    return JsonResponse({'institutions': list_institutions()})
