from django.http import JsonResponse
from django.utils import timezone

import plantit.queries as q
from plantit.users.models import Contributor
from plantit.misc.models import NewsUpdate, MaintenanceWindow


def updates(request):
    return JsonResponse({'updates': [q.update_to_dict(u) for u in list(NewsUpdate.objects.all().order_by('created'))]})


def maintenance_windows(request):
    # get only maintenance windows occurring today or in the future
    windows = list(MaintenanceWindow.objects.filter(end__gte=timezone.now()))
    return JsonResponse({'windows': [{'start': w.start.isoformat(), 'end': w.end.isoformat()} for w in windows]})


def contributors(request):
    contribs = list(Contributor.objects.all())
    return JsonResponse({'contributors': [q.contributor_to_dict(c) for c in contribs]})
