import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseNotFound
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

import plantit.queries as q
from plantit.redis import RedisClient


@swagger_auto_schema(methods='get')
@login_required
@api_view(['get'])
def institutions_info(_):
    redis = RedisClient.get()
    cached = list(redis.scan_iter(match=f"institutions/*"))
    if len(cached) > 0:
        institutions = [json.loads(redis.get(institution)) for institution in cached if institution is not None]
    else:
        institutions = q.get_institutions()
        for name, institution in institutions.items(): redis.set(f"institutions/{name}", json.dumps(institution))
    return JsonResponse({'institutions': institutions})


@swagger_auto_schema(methods='get')
@login_required
@api_view(['get'])
def aggregate_counts(_):
    redis = RedisClient.get()
    cached = redis.get("stats_counts")

    if cached is not None:
        counts = json.loads(cached)
    else:
        counts = q.get_total_counts()
        redis.set("stats_counts", json.dumps(counts))

    return JsonResponse(counts)


@swagger_auto_schema(methods='get')
@login_required
@api_view(['get'])
def aggregate_timeseries(_):
    redis = RedisClient.get()
    cached = redis.get("total_timeseries")

    if cached is not None:
        series = json.loads(cached)
    else:
        series = q.get_aggregate_timeseries()
        redis.set("total_timeseries", json.dumps(series))

    return JsonResponse(series)


@login_required
def workflow_timeseries(_, owner, name, branch):
    redis = RedisClient.get()
    cached = redis.get(f"workflow_timeseries/{owner}/{name}/{branch}")

    if cached is not None:
        series = json.loads(cached)
    else:
        series = q.get_workflow_usage_timeseries(owner, name, branch)
        redis.set(f"workflow_timeseries/{owner}/{name}/{branch}", json.dumps(series))

    return JsonResponse(series)


@login_required
def user_timeseries(request, username):
    try: user = User.objects.get(username=username)
    except: return HttpResponseNotFound()

    redis = RedisClient.get()
    cached = redis.get(f"user_timeseries/{user.username}")

    if cached is not None:
        series = json.loads(cached)
    else:
        series = q.get_user_timeseries(user)
        redis.set(f"user_timeseries/{user.username}", json.dumps(series))

    return JsonResponse(series)
