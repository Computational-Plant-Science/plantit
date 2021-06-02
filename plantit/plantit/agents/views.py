import logging
import uuid
from datetime import timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse, HttpResponseForbidden
from django.utils import timezone
from rest_framework.decorators import api_view

from plantit.ssh import SSH, execute_command
from plantit.agents.models import Agent, AgentAccessPolicy, AgentRole, AgentAccessRequest
from plantit.agents.utils import map_agent
from plantit.notifications.models import TargetPolicyNotification

logger = logging.getLogger(__name__)


@api_view(['GET', 'POST'])
@login_required
def search_or_add(request):
    if request.method == 'GET':
        agents = Agent.objects.all()
        public = request.GET.get('public')
        agent_name = request.GET.get('name')
        agent_owner = request.GET.get('owner')

        if public is not None and bool(public):
            logger.info(f"Filtering agents by {'public' if bool(public) else 'private'} visibility")
            agents = agents.filter(public=bool(public))
        if agent_name is not None and type(agent_name) is str:
            logger.info(f"Filtering agents by name: {agent_name}")
            agents = agents.filter(name=agent_name)
        if agent_owner is not None and type(agent_owner) is str:
            logger.info(f"Filtering agents by owner: {agent_owner}")
            try:
                agents = agents.filter(user=User.objects.get(username=agent_owner))
            except:
                return HttpResponseNotFound()

        return JsonResponse({'agents': [map_agent(agent, AgentRole.admin) for agent in agents]})
    elif request.method == 'POST':
        # make sure we can authenticate
        ssh = SSH(
            host=request.data['config']['hostname'],
            port=22,
            username=request.data['auth']['username'],
            password=request.data['auth']['password'])
        with ssh:
            execute_command(
                ssh_client=ssh,
                pre_command=request.data['config']['pre_commands'],
                command='pwd',
                directory=request.data['config']['workdir'],
                allow_stderr=False)

        config = request.data['config']
        guid = str(uuid.uuid4())
        name = config['name'] if 'name' in config else None
        executor = str(config['executor']).lower()
        agent, created = Agent.objects.get_or_create(
            name=guid if name is None else name,
            guid=guid,
            user=request.user,
            description=config['description'],
            workdir=config['workdir'],
            username=request.user.username,
            port=22,
            hostname=config['hostname'],
            pre_commands=config['pre_commands'],
            max_time=timedelta(hours=int(config['max_time'])),
            disabled=False,
            public=bool(config['public']),
            logo=config['logo'],
            callbacks=False,
            executor=executor)

        if created:
            if executor != 'local':
                agent.max_walltime = int(config['max_walltime'])
                agent.max_mem = int(config['max_mem'])
                agent.max_cores = int(config['max_cores'])
                agent.max_nodes = int(config['max_nodes'])
                agent.queue = config['queue']
                agent.project = config['project']
                agent.header_skip = config['header_skip']
                agent.gpu = bool(config['gpu'])
                agent.gpu_queue = config['gpu_queue']
                agent.job_array = bool(config['job_array'])
                agent.launcher = bool(config['launcher'])
                agent.save()

            policy = AgentAccessPolicy.objects.create(user=request.user, agent=agent, role=AgentRole.admin)
            return JsonResponse({'created': created, 'agent': map_agent(agent, policy.role)})

        return JsonResponse({'created': created, 'agent': map_agent(agent)})


@api_view(['GET'])
@login_required
def get_by_name(request, name):
    try:
        agent = Agent.objects.get(name=name)
    except:
        return HttpResponseNotFound()

    policies = AgentAccessPolicy.objects.filter(agent=agent)

    try:
        access_requests = AgentAccessRequest.objects.filter(agent=agent)
    except:
        access_requests = None

    if agent not in [policy.agent for policy in policies]:
        return JsonResponse(map_agent(agent, AgentRole.none, None, access_requests))

    try:
        role = AgentAccessPolicy.objects.get(user=request.user, agent=agent).role
    except:
        role = AgentRole.none

    return JsonResponse(map_agent(agent, role, list(policies), access_requests))


@api_view(['GET'])
@login_required
def exists(request, name):
    try:
        Agent.objects.get(name=name)
        return JsonResponse({'exists': True})
    except:
        return JsonResponse({'exists': False})


@api_view(['GET'])
@login_required
def host_exists(request, host):
    try:
        Agent.objects.get(hostname=host)
        return JsonResponse({'exists': True})
    except:
        return JsonResponse({'exists': False})


@api_view(['POST'])
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


@api_view(['POST'])
@login_required
def grant_access(request, name):
    user_name = request.data['user']
    if name is None or user_name is None:
        return HttpResponseNotFound()

    try:
        agent = Agent.objects.get(name=name)
        user = User.objects.get(owner=user_name)
    except:
        return HttpResponseNotFound()

    if agent.user is not None and agent.user.username != request.user.username:
        return HttpResponseForbidden()

    policy, created = AgentAccessPolicy.objects.get_or_create(user=user, agent=agent, role=AgentRole.run)
    access_request = AgentAccessRequest.objects.get(user=user, agent=agent)
    access_request.delete()

    notification = TargetPolicyNotification.objects.create(
        guid=str(uuid.uuid4()),
        user=user,
        created=timezone.now(),
        policy=policy,
        message=f"You were granted access to {policy.agent.name}")
    async_to_sync(get_channel_layer().group_send)(f"notifications-{user.username}", {
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


@api_view(['POST'])
@login_required
def revoke_access(request, name):
    user_name = request.data['user']
    if name is None or user_name is None:
        return HttpResponseNotFound()

    try:
        agent = Agent.objects.get(name=name)
        user = User.objects.get(owner=user_name)
        policy = AgentAccessPolicy.objects.get(user=user, agent=agent)
    except:
        return HttpResponseNotFound()

    if agent.user is not None and agent.user.username != request.user.username:
        return HttpResponseForbidden()

    notification = TargetPolicyNotification.objects.create(
        guid=str(uuid.uuid4()),
        user=user,
        created=timezone.now(),
        policy=policy,
        message=f"Your access to {policy.agent.name} was revoked")
    async_to_sync(get_channel_layer().group_send)(f"notifications-{user.username}", {
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

    policy.delete()
    return HttpResponse()


@api_view(['POST'])
@login_required
def toggle_public(request, name):
    if name is None:
        return HttpResponseNotFound()

    try:
        agent = Agent.objects.get(name=name)
    except:
        return HttpResponseNotFound()

    agent.public = not agent.public
    agent.save()

    return JsonResponse({'public': agent.public})


@api_view(['GET'])
@login_required
def get_status(request, name):
    try:
        agent = Agent.objects.get(name=name)
    except:
        return HttpResponseNotFound()

    try:
        ssh = SSH(agent.hostname, agent.port, agent.username)
        with ssh:
            lines = execute_command(
                ssh_client=ssh,
                pre_command=':',
                command=f"pwd",
                directory=agent.workdir)
            print(lines)
            return JsonResponse({'healthy': True})
    except:
        return JsonResponse({'healthy': False})


@api_view(['GET'])
@login_required
def get_users(request, name):
    try:
        agent = Agent.objects.get(name=name)
    except:
        return HttpResponseNotFound()

    return JsonResponse({'policies': list(AgentAccessPolicy.objects.filter(agent=agent))})
