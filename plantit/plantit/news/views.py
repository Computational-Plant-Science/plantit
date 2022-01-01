from django.http import JsonResponse

from plantit.news.models import NewsUpdate
from plantit.utils import update_to_dict


def updates(request):
    return JsonResponse({'updates': [update_to_dict(u) for u in list(NewsUpdate.objects.all().order_by('created'))]})
