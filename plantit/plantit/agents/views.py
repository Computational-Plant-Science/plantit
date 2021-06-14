import json
import logging
import traceback
import uuid
from datetime import timedelta

from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseBadRequest
from django.utils import timezone

from plantit.ssh import SSH, execute_command
from plantit.agents.models import Agent, AgentAccessPolicy, AgentRole, AgentAccessRequest, AgentAuthentication
from plantit.agents.utils import map_agent
from plantit.users.utils import get_or_create_keypair, get_private_key_path
from plantit.notifications.models import TargetPolicyNotification

logger = logging.getLogger(__name__)


@login_required
def list_or_bind(request):
    if request.method == 'GET':
        agents = Agent.objects.all()
        public = request.GET.get('public')
        agent_name = request.GET.get('name')
        agent_owner = request.GET.get('owner')

        if public is not None and bool(public): agents = agents.filter(public=bool(public))
        if agent_name is not None and type(agent_name) is str: agents = agents.filter(name=agent_name)
        if agent_owner is not None and type(agent_owner) is str:
            try: agents = agents.filter(user=User.objects.get(username=agent_owner))
            except: return HttpResponseNotFound()

        return JsonResponse({'agents': [map_agent(agent, AgentRole.admin) for agent in agents]})
    elif request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))
        auth = body['auth']
        config = body['config']
        guid = str(uuid.uuid4())
        name = config['name'] if 'name' in config else None
        authentication = str(config['authentication']).lower()
        executor = str(config['executor']).lower()
        agent, created = Agent.objects.get_or_create(
            name=guid if name is None else name,
            guid=guid,
            user=request.user,
            description=config['description'],
            workdir=config['workdir'],
            username=auth['username'],
            port=22,
            hostname=config['hostname'],
            pre_commands=config['pre_commands'],
            max_time=timedelta(hours=int(config['max_time'])),
            disabled=False,
            public=bool(config['public']),
            logo=config['logo'],
            callbacks=False,
            executor=executor,
            authentication=authentication)

        if created:
            if executor != 'local':
                agent.max_walltime = int(config['max_walltime'])
                agent.max_mem = int(config['max_mem'])
                agent.max_cores = int(config['max_cores'])
                agent.max_nodes = int(config['max_nodes'])
                agent.queue = config['queue']
                agent.project = config['project']
                agent.header_skip = config['header_skip']
                # agent.gpu = bool(config['gpu'])
                # agent.gpu_queue = config['gpu_queue']
                agent.job_array = bool(config['job_array'])
                agent.launcher = bool(config['launcher'])
                agent.save()

            policy = AgentAccessPolicy.objects.create(user=request.user, agent=agent, role=AgentRole.admin)
            return JsonResponse({'created': created, 'agent': map_agent(agent, policy.role)})

        return JsonResponse({'created': created, 'agent': map_agent(agent)})


@login_required
def get_or_unbind(request, name):
    try: agent = Agent.objects.get(name=name)
    except: return HttpResponseNotFound()

    if request.method == 'GET':
        policies = AgentAccessPolicy.objects.filter(agent=agent)
        try: access_requests = AgentAccessRequest.objects.filter(agent=agent)
        except: access_requests = None

        if agent not in [policy.agent for policy in policies]:
            return JsonResponse(map_agent(agent, AgentRole.none, None, access_requests))

        try: role = AgentAccessPolicy.objects.get(user=request.user, agent=agent).role
        except: role = AgentRole.none
        return JsonResponse(map_agent(agent, role, list(policies), access_requests))
    elif request.method == 'DELETE':
        agent.delete()
        logger.info(f"Removed binding for agent {name}")
        agents = Agent.objects.filter(user=request.user)
        return JsonResponse({'agents': [map_agent(agent, AgentRole.admin) for agent in agents]})



@login_required
def exists(request, name):
    try:
        Agent.objects.get(name=name)
        return JsonResponse({'exists': True})
    except:
        return JsonResponse({'exists': False})


@login_required
def host_exists(request, host):
    try:
        Agent.objects.get(hostname=host)
        return JsonResponse({'exists': True})
    except:
        return JsonResponse({'exists': False})


@login_required
def request_access(request, name):
    if name is None:
        return HttpResponseNotFound()

    try:
        agent = Agent.objects.get(name=name)
    except:
        return HttpResponseNotFound()

    _, created = AgentAccessRequest.objects.get_or_create(user=request.user, agent=agent)
    return JsonResponse({
        'created': created
    })


@sync_to_async
@login_required
@async_to_sync
async def grant_access(request, name):
    body = json.loads(request.body.decode('utf-8'))
    user_name = body['user']
    if name is None or user_name is None:
        return HttpResponseNotFound()

    try:
        agent = await sync_to_async(Agent.objects.get)(name=name)
        user = await sync_to_async(User.objects.get)(owner=user_name)
    except:
        return HttpResponseNotFound()

    if agent.user is not None and agent.user.username != request.user.username:
        return HttpResponseForbidden()

    policy, created = await sync_to_async(AgentAccessPolicy.objects.get_or_create)(user=user, agent=agent, role=AgentRole.run)
    access_request = await sync_to_async(AgentAccessRequest.objects.get)(user=user, agent=agent)
    await sync_to_async(access_request.delete)()

    notification = await sync_to_async(TargetPolicyNotification.objects.create)(
        guid=str(uuid.uuid4()),
        user=user,
        created=timezone.now(),
        policy=policy,
        message=f"You were granted access to {policy.agent.name}")

    await get_channel_layer().group_send(f"notifications-{user.username}", {
        'type': 'push_notification',
        'notification': {
            'id': notification.guid,
            'username': notification.user.username,
            'created': notification.created.isoformat(),
            'message': notification.message,
            'read': notification.read,
            'policy': {
                'user': user.username,
                'role': str(notification.policy.role)
            }
        }
    })

    return JsonResponse({'granted': created})


@login_required
async def revoke_access(request, name):
    body = json.loads(request.body.decode('utf-8'))
    user_name = body['user']
    if name is None or user_name is None:
        return HttpResponseNotFound()

    try:
        agent = await sync_to_async(Agent.objects.get)(name=name)
        user = await sync_to_async(User.objects.get)(owner=user_name)
        policy = await sync_to_async(AgentAccessPolicy.objects.get)(user=user, agent=agent)
    except:
        return HttpResponseNotFound()

    if agent.user is not None and agent.user.username != request.user.username:
        return HttpResponseForbidden()

    notification = await sync_to_async(TargetPolicyNotification.objects.create)(
        guid=str(uuid.uuid4()),
        user=user,
        created=timezone.now(),
        policy=policy,
        message=f"Your access to {policy.agent.name} was revoked")

    await get_channel_layer().group_send(f"notifications-{user.username}", {
        'type': 'push_notification',
        'notification': {
            'id': notification.guid,
            'username': notification.user.username,
            'created': notification.created.isoformat(),
            'message': notification.message,
            'read': notification.read,
            'policy': {
                'user': user.username,
                'role': str(notification.policy.role)
            }
        }
    })

    await sync_to_async(policy.delete)()
    return HttpResponse()


@login_required
def toggle_public(request, name):
    try:
        agent = Agent.objects.get(name=name)
    except:
        return HttpResponseNotFound()

    if agent.user is not None and agent.user.username != request.user.username:
        return HttpResponseForbidden()

    agent.public = not agent.public
    agent.save()
    logger.info(f"Agent {name} is now {'public' if agent.public else 'private'}")

    return JsonResponse({'agents': [map_agent(agent, AgentRole.admin) for agent in list(Agent.objects.filter(user=request.user))]})


@login_required
def healthcheck(request, name):
    try: agent = Agent.objects.get(name=name)
    except: return HttpResponseNotFound()

    body = json.loads(request.body.decode('utf-8'))

    try:
        if agent.authentication == AgentAuthentication.PASSWORD:
            try:
                username = body['auth']['username']
                password = body['auth']['password']
            except: return HttpResponseBadRequest()
            ssh = SSH(host=agent.hostname, port=22, username=username, password=password)
        else:
            logger.info(str(get_private_key_path(request.user.username)))
            ssh = SSH(host=agent.hostname, port=22, username=agent.username, pkey=str(get_private_key_path(request.user.username)))

        with ssh:
            logger.info(f"Checking agent {agent.name}'s health")
            for line in execute_command(ssh=ssh, precommand=':', command=f"pwd", directory=agent.workdir): logger.info(line)
            logger.info(f"Agent {agent.name} healthcheck succeeded")
            return JsonResponse({'healthy': True})
    except:
        logger.warning(f"Agent {agent.name} healthcheck failed:\n{traceback.format_exc()}")
        return JsonResponse({'healthy': False})


@login_required
def get_access_policies(request, name):
    try:
        agent = Agent.objects.get(name=name)
    except:
        return HttpResponseNotFound()

    return JsonResponse({'policies': list(AgentAccessPolicy.objects.filter(agent=agent))})


@login_required
def set_authentication_strategy(request, name):
    body = json.loads(request.body.decode('utf-8'))
    try:
        strategy = body['strategy']
        authentication = AgentAuthentication.PASSWORD if strategy == 'password' else AgentAuthentication.KEY
    except: return HttpResponseBadRequest()

    try: agent = Agent.objects.get(name=name)
    except: return HttpResponseNotFound()

    agent.authentication = authentication
    agent.save()
    logger.info(f"Agent {name} is now using {authentication} authentication")

    return JsonResponse({'agents': [map_agent(agent, AgentRole.admin) for agent in list(Agent.objects.filter(user=request.user))]})
