import json

from asgiref.sync import sync_to_async, async_to_sync
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseNotFound
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

import plantit.mapbox
import plantit.queries as q
from plantit.redis import RedisClient


@swagger_auto_schema(methods='get')
@api_view(['get'])
def institutions_info(request):
    invalidate = request.GET.get('invalidate', False)
    return JsonResponse(q.get_institutions(invalidate))


@swagger_auto_schema(methods='get')
@api_view(['get'])
def aggregate_counts(request):
    invalidate = request.GET.get('invalidate', False)
    return JsonResponse(q.get_total_counts(invalidate))


@swagger_auto_schema(methods='get')
@api_view(['get'])
def aggregate_timeseries(request):
    invalidate = request.GET.get('invalidate', False)
    return JsonResponse(q.get_aggregate_timeseries(invalidate))


@swagger_auto_schema(methods='get')
@api_view(['get'])
def workflow_timeseries(request, owner, name, branch):
    invalidate = request.GET.get('invalidate', False)
    return JsonResponse(q.get_workflow_usage_timeseries(owner, name, branch, invalidate))


@login_required
def user_timeseries(request, username):
    try: user = User.objects.get(username=username)
    except: return HttpResponseNotFound()
    return JsonResponse(q.get_user_timeseries(user))
