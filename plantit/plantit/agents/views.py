import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseNotFound
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

from plantit.agents.models import Agent, AgentAccessPolicy
from plantit.cache import ModelViews
from plantit.health import is_healthy
from plantit.redis import RedisClient

logger = logging.getLogger(__name__)


def authorized_for_agent(agent: Agent, user: User):
    authorized_users = [u.username for u in agent.users_authorized.all()]

    # if agent isn't public, requesting user doesn't own it, and isn't
    # on list of authorized users, they aren't authorized to access it
    return (agent.public or
            agent.user == user or
            user.username in authorized_users)


@swagger_auto_schema(methods='get')
@login_required
@api_view(['GET'])
def list(request):
    user = request.user
    views = ModelViews(cache=RedisClient.get())
    agents = views.get_agents(user)
    return JsonResponse({'agents': [ModelViews.agent_to_dict(agent, user.username) for agent in agents]})


@swagger_auto_schema(method='get', auto_schema=None)
@login_required
@api_view(['GET'])
def get(request, name):
    try:
        agent = Agent.objects.get(name=name)
        if not authorized_for_agent(agent=agent, user=request.user):
            return HttpResponseNotFound()
    except:
        return HttpResponseNotFound()

    return JsonResponse(ModelViews.agent_to_dict(agent, request.user.username))


@swagger_auto_schema(method='get', auto_schema=None)
@login_required
@api_view(['GET'])
def exists(request, name):
    try:
        agent = Agent.objects.get(name=name)
        return JsonResponse({'exists': authorized_for_agent(agent=agent, user=request.user)})
    except:
        return JsonResponse({'exists': False})


@swagger_auto_schema(method='post', auto_schema=None)
@login_required
@api_view(['POST'])
def healthcheck(request, name):
    try:
        agent = Agent.objects.get(name=name)
        if not authorized_for_agent(agent=agent, user=request.user):
            return HttpResponseNotFound()
    except:
        return HttpResponseNotFound()

    healthy, output = is_healthy(agent)
    check = {
        'timestamp': timezone.now().isoformat(),
        'healthy': healthy,
        'output': output
    }

    # persist health status to DB
    agent.is_healthy = healthy
    agent.save()

    # update cache
    redis = RedisClient.get()
    length = redis.llen(f"healthchecks/{agent.name}")
    checks_saved = int(settings.AGENTS_HEALTHCHECKS_SAVED)
    if length > checks_saved: redis.rpop(f"healthchecks/{agent.name}")
    redis.lpush(f"healthchecks/{agent.name}", json.dumps(check))
    return JsonResponse(check)


@swagger_auto_schema(method='get', auto_schema=None)
@login_required
@api_view(['GET'])
def healthchecks(request, name):
    try:
        agent = Agent.objects.get(name=name)
        if not authorized_for_agent(agent=agent, user=request.user):
            return HttpResponseNotFound()
    except:
        return HttpResponseNotFound()

    redis = RedisClient.get()
    checks = [json.loads(check) for check in redis.lrange(f"healthchecks/{agent.name}", 0, -1)]
    return JsonResponse({'healthchecks': checks})


@swagger_auto_schema(method='get', auto_schema=None)
@login_required
@api_view(['GET'])
def policies(request, name):
    try:
        agent = Agent.objects.get(name=name)
        if not authorized_for_agent(agent=agent, user=request.user):
            return HttpResponseNotFound()
    except:
        return HttpResponseNotFound()

    return JsonResponse({'policies': list(AgentAccessPolicy.objects.filter(agent=agent))})
