from django.contrib.auth.models import User
from django.http import JsonResponse

from plantit.tasks.models import Task
from plantit.workflows.models import Workflow


def counts(request):
    return JsonResponse({
        'users': User.objects.count(),
        'workflows': Workflow.objects.count(),
        'tasks': Task.objects.count()
    })
