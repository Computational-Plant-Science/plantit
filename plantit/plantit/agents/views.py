import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotFound
from django.utils import timezone

from plantit.agents.models import Agent, AgentAccessPolicy
from plantit.utils import agent_to_dict, is_healthy
from plantit.redis import RedisClient

logger = logging.getLogger(__name__)


@login_required
def list(request):
    return JsonResponse({'agents': [agent_to_dict(agent, request.user) for agent in Agent.objects.all()]})


@login_required
def get(request, name):
    try: agent = Agent.objects.get(name=name)
    except: return HttpResponseNotFound()
    return JsonResponse(agent_to_dict(agent, request.user))


@login_required
def exists(request, name):
    try:
        Agent.objects.get(name=name)
        return JsonResponse({'exists': True})
    except: return JsonResponse({'exists': False})


@login_required
def healthcheck(request, name):
    try: agent = Agent.objects.get(name=name)
    except: return HttpResponseNotFound()

    body = json.loads(request.body.decode('utf-8'))
    healthy, output = is_healthy(agent, body['auth'])
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


@login_required
def healthchecks(request, name):
    redis = RedisClient.get()
    checks = [json.loads(check) for check in redis.lrange(f"healthchecks/{name}", 0, -1)]
    return JsonResponse({'healthchecks': checks})


@login_required
def policies(request, name):
    try: agent = Agent.objects.get(name=name)
    except: return HttpResponseNotFound()
    return JsonResponse({'policies': list(AgentAccessPolicy.objects.filter(agent=agent))})
