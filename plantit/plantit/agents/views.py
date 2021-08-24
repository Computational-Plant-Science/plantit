import json
import logging
import traceback
import uuid
from datetime import timedelta

from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseForbidden, HttpResponseBadRequest, HttpResponse
from django.utils import timezone

from plantit.agents.models import Agent, AgentAccessPolicy, AgentRole, AgentAuthentication
from plantit.notifications.models import Notification
from plantit.ssh import SSH, execute_command
from plantit.utils import agent_to_dict, get_agent_user, agent_to_dict_async, get_user_private_key_path, is_healthy
from plantit.workflows.models import Workflow

logger = logging.getLogger(__name__)


@login_required
def list_or_bind(request):
    if request.method == 'GET':
        agents = Agent.objects.all()
        public = request.GET.get('public')
        agent_name = request.GET.get('name')
        agent_owner = request.GET.get('owner', None)
        agent_guest = request.GET.get('guest', None)

        if agent_owner is not None and agent_guest is not None:
            return HttpResponseBadRequest('Expected either \'owner\' or \'guest\' query param, not both')

        if public is not None and bool(public): agents = agents.filter(public=bool(public))
        if agent_name is not None and type(agent_name) is str: agents = agents.filter(name=agent_name)
        if agent_owner is not None and type(agent_owner) is str:
            try:
                agents = agents.filter(user=User.objects.get(username=agent_owner))
            except: return HttpResponseNotFound()
        elif agent_guest is not None and type(agent_guest) is str:
            try:
                agents = agents.filter(users_authorized__username__exact=agent_guest)
            except: return HttpResponseNotFound()

        return JsonResponse({'agents': [agent_to_dict(agent, request.user) for agent in agents]})
    elif request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))
        auth = body['auth']
        config = body['config']
        guid = str(uuid.uuid4())
        name = config['name'] if 'name' in config else None
        authentication = str(config['authentication']).lower()
        executor = str(config['executor']).lower()

        # get workdir
        if 'password' in auth:
            ssh = SSH(auth['hostname'], port=auth['port'], username=auth['username'], password=auth['password'])
        else:
            pkey = str(get_user_private_key_path(request.user.username))
            ssh = SSH(auth['hostname'], port=auth['port'], username=auth['username'], pkey=pkey)

        workdir = None
        with ssh:
            for line in execute_command(ssh=ssh, precommand=':', command='pwd', directory=f"{config['workdir']}/.plantit", allow_stderr=False): workdir = line
            if workdir is None or '.plantit' not in workdir: return HttpResponse(status=500)
        # workdir = workdir.rpartition('/')[0]

        agent, created = Agent.objects.get_or_create(
            name=guid if name is None else name,
            guid=guid,
            user=request.user,
            description=config['description'],
            workdir=workdir.strip(),
            username=auth['username'],
            port=auth['port'],
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

            return JsonResponse({'created': created, 'agent': agent_to_dict(agent, request.user)})

        return JsonResponse({'created': created, 'agent': agent_to_dict(agent, request.user)})


@login_required
def get_or_unbind(request, name):
    try: agent = Agent.objects.get(name=name)
    except: return HttpResponseNotFound()

    if request.method == 'GET':
        return JsonResponse(agent_to_dict(agent, request.user))
    elif request.method == 'DELETE':
        agent.delete()
        logger.info(f"Removed binding for agent {name}")
        agents = Agent.objects.filter(user=request.user)
        return JsonResponse({'agents': [agent_to_dict(agent, request.user) for agent in agents]})



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


@sync_to_async
@login_required
@async_to_sync
async def authorize_user(request, name):
    body = json.loads(request.body.decode('utf-8'))
    user_name = body['user']
    if name is None or user_name is None:
        return HttpResponseNotFound()

    try:
        agent = await sync_to_async(Agent.objects.get)(name=name)
        user = await sync_to_async(User.objects.get)(username=user_name)
    except:
        return HttpResponseNotFound()

    agent_user = await get_agent_user(agent)
    if agent_user is not None and agent_user.username != request.user.username:
        return HttpResponseForbidden()

    await sync_to_async(agent.users_authorized.add)(user)
    await sync_to_async(agent.save)()

    notification = await sync_to_async(Notification.objects.create)(
        guid=str(uuid.uuid4()),
        user=user,
        created=timezone.now(),
        message=f"You were granted access to agent {agent.name}")

    await get_channel_layer().group_send(f"notifications-{user.username}", {
        'type': 'push_notification',
        'notification': {
            'id': notification.guid,
            'username': notification.user.username,
            'created': notification.created.isoformat(),
            'message': notification.message,
            'read': notification.read,
        }
    })
    output = await agent_to_dict_async(agent, request.user)
    return JsonResponse(output)


@sync_to_async
@login_required
@async_to_sync
async def unauthorize_user(request, name):
    body = json.loads(request.body.decode('utf-8'))
    user_name = body['user']
    if name is None or user_name is None:
        return HttpResponseNotFound()

    try:
        agent = await sync_to_async(Agent.objects.get)(name=name)
        user = await sync_to_async(User.objects.get)(username=user_name)
    except:
        return HttpResponseNotFound()

    agent_user = await get_agent_user(agent)
    if agent_user is not None and agent_user.username != request.user.username:
        return HttpResponseForbidden()

    await sync_to_async(agent.users_authorized.remove)(user)
    await sync_to_async(agent.save)()

    notification = await sync_to_async(Notification.objects.create)(
        guid=str(uuid.uuid4()),
        user=user,
        created=timezone.now(),
        message=f"Your access to agent {agent.name} was revoked")

    await get_channel_layer().group_send(f"notifications-{user.username}", {
        'type': 'push_notification',
        'notification': {
            'id': notification.guid,
            'username': notification.user.username,
            'created': notification.created.isoformat(),
            'message': notification.message,
            'read': notification.read,
        }
    })
    output = await agent_to_dict_async(agent, request.user)
    return JsonResponse(output)


@login_required
def authorize_workflow(request, name):
    body = json.loads(request.body.decode('utf-8'))
    workflow_owner = body.get('owner', None)
    workflow_name = body.get('name', None)
    if workflow_name is None or workflow_owner is None or workflow_name is None:
        return HttpResponseBadRequest()

    try:
        agent = Agent.objects.get(name=name)
        workflow = Workflow.objects.get(repo_owner=workflow_owner, repo_name=workflow_name)
    except:
        return HttpResponseNotFound()

    if agent.user is not None and agent.user.username != request.user.username:
        return HttpResponseForbidden()

    agent.workflows_authorized.add(workflow)
    agent.save()

    return JsonResponse(agent_to_dict(agent, request.user))


@login_required
def unauthorize_workflow(request, name):
    body = json.loads(request.body.decode('utf-8'))
    workflow_owner = body.get('owner', None)
    workflow_name = body.get('name', None)
    if workflow_name is None or workflow_owner is None or workflow_name is None:
        return HttpResponseBadRequest()

    try:
        agent = Agent.objects.get(name=name)
        workflow = Workflow.objects.get(repo_owner=workflow_owner, repo_name=workflow_name)
    except:
        return HttpResponseNotFound()

    if agent.user is not None and agent.user.username != request.user.username:
        return HttpResponseForbidden()

    agent.workflows_authorized.remove(workflow)
    agent.save()

    return JsonResponse(agent_to_dict(agent, request.user))


@login_required
def block_workflow(request, name):
    body = json.loads(request.body.decode('utf-8'))
    workflow_owner = body.get('owner', None)
    workflow_name = body.get('name', None)
    if workflow_name is None or workflow_owner is None or workflow_name is None:
        return HttpResponseBadRequest()

    try:
        agent = Agent.objects.get(name=name)
        workflow = Workflow.objects.get(repo_owner=workflow_owner, repo_name=workflow_name)
    except:
        return HttpResponseNotFound()

    if agent.user is not None and agent.user.username != request.user.username:
        return HttpResponseForbidden()

    agent.workflows_blocked.add(workflow)
    agent.save()

    return JsonResponse(agent_to_dict(agent, request.user))


@login_required
def unblock_workflow(request, name):
    body = json.loads(request.body.decode('utf-8'))
    workflow_owner = body.get('owner', None)
    workflow_name = body.get('name', None)
    if workflow_name is None or workflow_owner is None or workflow_name is None:
        return HttpResponseBadRequest()

    try:
        agent = Agent.objects.get(name=name)
        workflow = Workflow.objects.get(repo_owner=workflow_owner, repo_name=workflow_name)
    except:
        return HttpResponseNotFound()

    if agent.user is not None and agent.user.username != request.user.username:
        return HttpResponseForbidden()

    agent.workflows_blocked.remove(workflow)
    agent.save()

    return JsonResponse(agent_to_dict(agent, request.user))


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

    return JsonResponse({'agents': [agent_to_dict(agent, request.user) for agent in list(Agent.objects.filter(user=request.user))]})


@login_required
def toggle_disabled(request, name):
    try:
        agent = Agent.objects.get(name=name)
    except:
        return HttpResponseNotFound()

    if agent.user is not None and agent.user.username != request.user.username:
        return HttpResponseForbidden()

    agent.disabled = not agent.disabled
    agent.save()
    logger.info(f"{'Disabled' if agent.disabled else 'Enabled'} {agent.name}")

    return JsonResponse(agent_to_dict(agent, request.user))


@login_required
def healthcheck(request, name):
    try: agent = Agent.objects.get(name=name)
    except: return HttpResponseNotFound()

    body = json.loads(request.body.decode('utf-8'))
    healthy, output = is_healthy(agent, body['auth'])
    return JsonResponse({'healthy': healthy, 'output': output})


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

    return JsonResponse({'agents': [agent_to_dict(agent, request.user) for agent in list(Agent.objects.filter(user=request.user))]})
