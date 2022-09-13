from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseNotFound
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

from plantit_web.cache import ModelViews
from plantit_web.redis import RedisClient


@swagger_auto_schema(methods='get')
@api_view(['get'])
def institutions_info(request):
    invalidate = request.GET.get('invalidate', False)
    views = ModelViews(cache=RedisClient.get())
    return JsonResponse(views.get_institutions(invalidate=invalidate))


@swagger_auto_schema(methods='get')
@api_view(['get'])
def aggregate_counts(request):
    invalidate = request.GET.get('invalidate', False)
    views = ModelViews(cache=RedisClient.get())
    return JsonResponse(views.get_total_counts(invalidate=invalidate))


@swagger_auto_schema(methods='get')
@api_view(['get'])
def aggregate_timeseries(request):
    invalidate = request.GET.get('invalidate', False)
    views = ModelViews(cache=RedisClient.get())
    return JsonResponse(views.get_aggregate_timeseries(invalidate=invalidate))


@swagger_auto_schema(methods='get')
@api_view(['get'])
def workflow_timeseries(request, owner, name, branch):
    invalidate = request.GET.get('invalidate', False)
    views = ModelViews(cache=RedisClient.get())
    return JsonResponse(views.get_workflow_usage_timeseries(owner, name, branch, invalidate))


@login_required
def user_timeseries(request):
    username = request.GET.get('username', request.user.username)
    try: user = User.objects.get(username=username)
    except: return HttpResponseNotFound()
    views = ModelViews(cache=RedisClient.get())
    return JsonResponse(views.get_user_timeseries(user))
