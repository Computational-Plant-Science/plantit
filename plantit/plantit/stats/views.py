from django.contrib.auth.models import User
from django.db.models import Count
from django.http import JsonResponse

from plantit.tasks.models import Task
from plantit.users.models import Profile
from plantit.workflows.models import Workflow


def counts(request):
    return JsonResponse({
        'users': User.objects.count(),
        'workflows': Workflow.objects.count(),
        'tasks': Task.objects.count()
    })


def institutions(request):
    institution_counts = list(Profile.objects.exclude(institution__exact='').values('institution').annotate(Count('institution')))
    return JsonResponse({'institutions': [{count['institution']: count['institution__count']} for count in institution_counts]})
