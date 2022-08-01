from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseNotFound, JsonResponse

from plantit.cache import ModelViews
from plantit.notifications.models import Notification
from plantit.redis import RedisClient


@login_required
def list_by_user(request, owner):
    try:
        params = request.query_params
    except:
        params = {}

    try: user = User.objects.get(username=owner)
    except: return HttpResponseNotFound()

    page = int(params.get('page') if 'page' in params else 1)
    views = ModelViews(cache=RedisClient.get())
    notifications = views.get_notifications_paged(user=user, page=page)
    return JsonResponse({'notifications': notifications})


@login_required
def get_or_dismiss(request, owner, guid):
    try:
        user = User.objects.get(username=owner)
        notification = Notification.objects.get(user=user, guid=guid)
    except: return HttpResponseNotFound()

    if request.method == 'GET':
        return JsonResponse(ModelViews.notification_to_dict(notification))
    elif request.method == 'DELETE':
        notification.delete()
        notifications = Notification.objects.filter(user=user)
        return JsonResponse({'notifications': [ModelViews.notification_to_dict(n) for n in notifications]})
