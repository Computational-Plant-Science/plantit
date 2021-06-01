import json
import logging
import uuid
from datetime import timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from plantit.ssh import SSH, execute_command
from plantit.agents.models import Agent, AgentAccessPolicy, AgentTask, AgentRole, AgentAccessRequest
from plantit.agents.serializers import AgentSerializer
from plantit.agents.utils import map_agent, map_agent_task
from plantit.notifications.models import TargetPolicyNotification


class AgentsViewSet(viewsets.ModelViewSet):
    queryset = Agent.objects.all()
    serializer_class = AgentSerializer
    permission_classes = (IsAuthenticated,)
    logger = logging.getLogger(__name__)

    @action(methods=['get'], detail=False)
    def get_by_query(self, request):
        agents = Agent.objects.all()
        public = request.GET.get('public')
        agent_name = request.GET.get('name')
        agent_owner = request.GET.get('owner')

        if public is not None and bool(public):
            self.logger.info(f"Filtering agents by {'public' if bool(public) else 'private'} visibility")
            agents = agents.filter(public=bool(public))
        if agent_name is not None and type(agent_name) is str:
            self.logger.info(f"Filtering agents by name: {agent_name}")
            agents = agents.filter(name=agent_name)
        if agent_owner is not None and type(agent_owner) is str:
            self.logger.info(f"Filtering agents by owner: {agent_owner}")
            try:
                agents = agents.filter(user=User.objects.get(username=agent_owner))
            except:
                return HttpResponseNotFound()

        return JsonResponse({'agents': [map_agent(agent, AgentRole.own) for agent in agents]})

    @action(methods=['get'], detail=False)
    def get_by_name(self, request):
        agent_name = request.GET.get('name')

        try:
            agent = Agent.objects.get(name=agent_name)
        except:
            return HttpResponseNotFound()

        user = request.user
        policies = AgentAccessPolicy.objects.filter(agent=agent)

        try:
            access_requests = AgentAccessRequest.objects.filter(agent=agent)
        except:
            access_requests = None

        if agent not in [policy.agent for policy in policies]:
            return JsonResponse(map_agent(agent, AgentRole.none, None, access_requests))

        try:
            role = AgentAccessPolicy.objects.get(user=user, agent=agent).role
        except:
            role = AgentRole.none
        return JsonResponse(map_agent(agent, role, list(policies), access_requests))

    @action(methods=['get'], detail=False)
    def get_by_username(self, request):
        user = request.user
        policies = AgentAccessPolicy.objects.filter(user=user, role__in=[AgentRole.own, AgentRole.run])
        agents = [map_agent(agent, policy.role, list(policies)) for agent, policy in
                  zip([policy.agent for policy in policies], policies) if policy.role != AgentRole.none]
        return JsonResponse({'agents': agents})

    @action(methods=['post'], detail=False)
    def connect(self, request):
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

        executor = str(request.data['config']['executor']).lower()
        agent, created = Agent.objects.get_or_create(
            name=request.data['config']['name'],
            guid=str(uuid.uuid4()),
            user=request.user,
            description=request.data['config']['description'],
            workdir=request.data['config']['workdir'],
            username=request.user.username,
            port=22,
            hostname=request.data['config']['hostname'],
            pre_commands=request.data['config']['pre_commands'],
            max_time=timedelta(hours=int(request.data['config']['max_time'])),
            disabled=False,
            public=bool(request.data['config']['public']),
            logo=request.data['config']['logo'],
            callbacks=False,
            executor=executor)

        if created:
            if executor != 'local':
                agent.max_walltime = int(request.data['config']['max_walltime'])
                agent.max_mem = int(request.data['config']['max_mem'])
                agent.max_cores = int(request.data['config']['max_cores'])
                agent.max_nodes = int(request.data['config']['max_nodes'])
                agent.queue = request.data['config']['queue']
                agent.project = request.data['config']['project']
                agent.header_skip = request.data['config']['header_skip']
                agent.gpu = bool(request.data['config']['gpu'])
                agent.gpu_queue = request.data['config']['gpu_queue']
                agent.job_array = bool(request.data['config']['job_array'])
                agent.launcher = bool(request.data['config']['launcher'])
                agent.save()

            policy = AgentAccessPolicy.objects.create(user=request.user, agent=agent, role=AgentRole.own)
            return JsonResponse({'created': created, 'agent': map_agent(agent, policy.role)})

        return JsonResponse({'created': created, 'agent': map_agent(agent)})

    @action(methods=['get'], detail=False)
    def grant_access(self, request):
        agent_name = request.GET.get('name', None)
        user_name = request.GET.get('user', None)

        if agent_name is None or user_name is None:
            return HttpResponseNotFound()

        try:
            agent = Agent.objects.get(name=agent_name)
            user = User.objects.get(owner=user_name)
        except:
            return HttpResponseNotFound()

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

    @action(methods=['get'], detail=False)
    def revoke_access(self, request):
        agent = request.GET.get('name', None)
        user_name = request.GET.get('user', None)

        if agent is None or user_name is None:
            return HttpResponseNotFound()

        try:
            agent = Agent.objects.get(name=agent)
            user = User.objects.get(owner=user_name)
            policy = AgentAccessPolicy.objects.get(user=user, agent=agent)
        except:
            return HttpResponseNotFound()

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

    @action(methods=['get'], detail=False)
    def request_access(self, request):
        agent_name = request.GET.get('name', None)
        if agent_name is None:
            return HttpResponseNotFound()

        try:
            agent = Agent.objects.get(name=agent_name)
        except:
            return HttpResponseNotFound()

        _, created = AgentAccessRequest.objects.get_or_create(user=request.user, agent=agent)
        return JsonResponse({
            'created': created
        })

    @action(methods=['get'], detail=False)
    def toggle_public(self, request):
        agent_name = request.GET.get('name', None)
        if agent_name is None:
            return HttpResponseNotFound()

        try:
            agent = Agent.objects.get(name=agent_name)
        except:
            return HttpResponseNotFound()

        agent.public = not agent.public
        agent.save()

        return JsonResponse({'public': agent.public})

    @action(methods=['get'], detail=False)
    def status(self, request):
        agent_name = request.GET.get('name')

        try:
            agent = Agent.objects.get(name=agent_name)
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

    @action(methods=['get'], detail=False)
    def get_users(self, request):
        agent_name = request.GET.get('name')

        try:
            agent = Agent.objects.get(name=agent_name)
        except:
            return HttpResponseNotFound()

        policies = AgentAccessPolicy.objects.filter(agent=agent)
        JsonResponse({'policies': list(policies)})

    @action(methods=['post'], detail=False)
    def create_task(self, request):
        try:
            agent_name = request.data['agent']
            agent = Agent.objects.get(name=agent_name)
        except:
            return HttpResponseNotFound()

        task_name = request.data['name']
        task_description = request.data['description']
        task_command = request.data['command']
        task_delay = request.data['delay'].split()

        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=task_delay[0],
            hour=task_delay[1],
            day_of_week=task_delay[2],
            day_of_month=task_delay[3],
            month_of_year=task_delay[4])
        task, created = AgentTask.objects.get_or_create(
            crontab=schedule,
            agent=agent,
            name=task_name,
            command=task_command,
            description=task_description,
            task='plantit.runs.tasks.execute_agent_command',
            args=json.dumps([agent.name, task_command]))

        return JsonResponse({
            'task': map_agent_task(task),
            'created': created
        })

    @action(methods=['get'], detail=False)
    def remove_task(self, request):
        task_name = request.GET.get('name', None)
        if task_name is None:
            return HttpResponseNotFound()

        try:
            task = PeriodicTask.objects.get(name=task_name)
        except:
            return HttpResponseNotFound()

        task.delete()
        return JsonResponse({'deleted': True})

    @action(methods=['get'], detail=False)
    def toggle_task(self, request):
        task_name = request.GET.get('name', None)
        if task_name is None:
            return HttpResponseNotFound()

        task = PeriodicTask.objects.get(name=task_name)
        task.enabled = not task.enabled
        task.save()
        return JsonResponse({'enabled': task.enabled})
