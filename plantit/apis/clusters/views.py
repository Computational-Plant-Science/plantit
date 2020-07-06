from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from plantit.jobs.models.cluster import Cluster


@login_required
def clusters(request):
    return JsonResponse({
        'clusters': [{
            'name': cluster.name,
            'description': cluster.description,
            'host': cluster.hostname
        } for cluster in Cluster.objects.all()]
    })
