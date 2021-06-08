import json
from itertools import chain

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseNotFound, JsonResponse

from plantit.notifications.models import TargetPolicyNotification, DirectoryPolicyNotification
from plantit.notifications.utils import map_notification


@login_required
def get_by_user(request, owner):
    try:
        params = request.query_params
    except:
        params = {}
    page = params.get('page') if 'page' in params else 0
    start = int(page) * 20
    count = start + 20

    try:
        user = User.objects.get(username=owner)
    except:
        return HttpResponseNotFound()

    notifications = list(chain(
        list(DirectoryPolicyNotification.objects.filter(user=user)),
        list(TargetPolicyNotification.objects.filter(user=user))))
    notifications = notifications[start:(start + count)]

    return JsonResponse({'notifications': [map_notification(n) for n in notifications]})


@login_required
def mark_many_read(request, owner):
    # TODO
    pass


@login_required
def mark_read(request, owner):
    user = request.user
    body = json.loads(request.body.decode('utf-8'))
    guid = body['notification']['id']

    try:
        notifications = list(chain(
            list(DirectoryPolicyNotification.objects.filter(user=user, guid=guid)),
            list(TargetPolicyNotification.objects.filter(user=user, guid=guid))))
        notification = notifications[0]
    except:
        return HttpResponseNotFound()

    notification.read = True
    notification.save()
    return JsonResponse({
        'notification': map_notification(notification)
    })
