from itertools import chain

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseNotFound, JsonResponse

import plantit.queries as q
from plantit.notifications.models import Notification


@login_required
def list_by_user(request, owner):
    try:
        params = request.query_params
    except:
        params = {}

    try: user = User.objects.get(username=owner)
    except: return HttpResponseNotFound()

    page = params.get('page') if 'page' in params else 1
    notifications = q.get_notifications(user, page=page)
    return JsonResponse({'notifications': notifications})


@login_required
def get_or_dismiss(request, owner, guid):
    try:
        user = User.objects.get(username=owner)
        notification = Notification.objects.get(user=user, guid=guid)
    except: return HttpResponseNotFound()

    if request.method == 'GET':
        return JsonResponse(q.notification_to_dict(notification))
    elif request.method == 'DELETE':
        notification.delete()
        notifications = Notification.objects.filter(user=user)
        return JsonResponse({'notifications': [q.notification_to_dict(notification) for notification in notifications]})
