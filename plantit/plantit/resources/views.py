import json
import uuid
from datetime import timedelta

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse, HttpResponseBadRequest
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from plantit.notifications.models import TargetPolicyNotification
from plantit.runs.ssh import SSH
from plantit.runs.utils import execute_command
from plantit.resources.models import Resource, ResourceAccessPolicy, ResourceTask, ResourceRole, ResourceAccessRequest
from plantit.resources.serializers import ResourceSerializer
from plantit.resources.utils import map_resource, map_resource_task


class ResourcesViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer
    permission_classes = (IsAuthenticated,)

    @action(methods=['get'], detail=False)
    def get_all(self, request):
        resources = list(Resource.objects.filter(public=True))
        return JsonResponse({'resources': [map_resource(resource) for resource in resources]})

    @action(methods=['post'], detail=False)
    def new(self, request):
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
        resource, created = Resource.objects.get_or_create(
            name=request.data['config']['name'],
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

        if created and executor != 'local':
            resource.max_walltime = int(request.data['config']['max_walltime'])
            resource.max_mem = int(request.data['config']['max_mem'])
            resource.max_cores = int(request.data['config']['max_cores'])
            resource.max_nodes = int(request.data['config']['max_nodes'])
            resource.queue = request.data['config']['queue']
            resource.project = request.data['config']['project']
            resource.header_skip = request.data['config']['header_skip']
            resource.gpu = bool(request.data['config']['gpu'])
            resource.gpu_queue = request.data['config']['gpu_queue']
            resource.job_array = bool(request.data['config']['job_array'])
            resource.launcher = bool(request.data['config']['launcher'])
            resource.save()

        return JsonResponse({'created': created, 'resource': map_resource(resource)})

    @action(methods=['get'], detail=False)
    def grant_access(self, request):
        resource_name = request.GET.get('name', None)
        user_name = request.GET.get('user', None)

        if resource_name is None or user_name is None:
            return HttpResponseNotFound()

        try:
            resource = Resource.objects.get(name=resource_name)
            user = User.objects.get(username=user_name)
        except:
            return HttpResponseNotFound()

        policy, created = ResourceAccessPolicy.objects.get_or_create(user=user, resource=resource, role=ResourceRole.run)
        access_request = ResourceAccessRequest.objects.get(user=user, resource=resource)
        access_request.delete()

        notification = TargetPolicyNotification.objects.create(
            guid=str(uuid.uuid4()),
            user=user,
            created=timezone.now(),
            policy=policy,
            message=f"You were granted access to {policy.resource.name}")
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
        resource_name = request.GET.get('name', None)
        user_name = request.GET.get('user', None)

        if resource_name is None or user_name is None:
            return HttpResponseNotFound()

        try:
            resource = Resource.objects.get(name=resource_name)
            user = User.objects.get(username=user_name)
            policy = ResourceAccessPolicy.objects.get(user=user, resource=resource)
        except:
            return HttpResponseNotFound()

        notification = TargetPolicyNotification.objects.create(
            guid=str(uuid.uuid4()),
            user=user,
            created=timezone.now(),
            policy=policy,
            message=f"Your access to {policy.resource.name} was revoked")
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
        resource_name = request.GET.get('name', None)
        if resource_name is None:
            return HttpResponseNotFound()

        try:
            resource = Resource.objects.get(name=resource_name)
        except:
            return HttpResponseNotFound()

        _, created = ResourceAccessRequest.objects.get_or_create(user=request.user, resource=resource)
        return JsonResponse({
            'created': created
        })

    @action(methods=['get'], detail=False)
    def toggle_public(self, request):
        resource_name = request.GET.get('name', None)
        if resource_name is None:
            return HttpResponseNotFound()

        try:
            resource = Resource.objects.get(name=resource_name)
        except:
            return HttpResponseNotFound()

        resource.public = not resource.public
        resource.save()

        return JsonResponse({'public': resource.public})

    @action(methods=['get'], detail=False)
    def get_by_name(self, request):
        resource_name = request.GET.get('name')

        try:
            resource = Resource.objects.get(name=resource_name)
        except:
            return HttpResponseNotFound()

        user = request.user
        policies = ResourceAccessPolicy.objects.filter(resource=resource)

        try:
            access_requests = ResourceAccessRequest.objects.filter(resource=resource)
        except:
            access_requests = None

        if resource not in [policy.resource for policy in policies]:
            return JsonResponse(map_resource(resource, ResourceRole.none, None, access_requests))

        try:
            role = ResourceAccessPolicy.objects.get(user=user, resource=resource).role
        except:
            role = ResourceRole.none
        return JsonResponse(map_resource(resource, role, list(policies), access_requests))

    @action(methods=['get'], detail=False)
    def status(self, request):
        name = request.GET.get('name')

        try:
            resource = Resource.objects.get(name=name)
        except:
            return HttpResponseNotFound()

        try:
            ssh = SSH(resource.hostname, resource.port, resource.username)
            with ssh:
                lines = execute_command(
                    ssh_client=ssh,
                    pre_command=':',
                    command=f"pwd",
                    directory=resource.workdir)
                print(lines)
                return JsonResponse({'healthy': True})
        except:
            return JsonResponse({'healthy': False})

    @action(methods=['get'], detail=False)
    def get_users(self, request):
        name = request.GET.get('name')

        try:
            resource = Resource.objects.get(name=name)
        except:
            return HttpResponseNotFound()

        policies = ResourceAccessPolicy.objects.filter(resource=resource)
        JsonResponse({'policies': list(policies)})

    @action(methods=['get'], detail=False)
    def get_by_username(self, request):
        user = request.user
        policies = ResourceAccessPolicy.objects.filter(user=user, role__in=[ResourceRole.own, ResourceRole.run])
        resources = [map_resource(resource, policy.role, list(policies)) for resource, policy in
                     zip([policy.resource for policy in policies], policies) if policy.role != ResourceRole.none]
        return JsonResponse({'resources': resources})

    @action(methods=['post'], detail=False)
    def create_task(self, request):
        try:
            resource_name = request.data['resource']
            resource = Resource.objects.get(name=resource_name)
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
        task, created = ResourceTask.objects.get_or_create(
            crontab=schedule,
            resource=resource,
            name=task_name,
            command=task_command,
            description=task_description,
            task='plantit.runs.tasks.run_command',
            args=json.dumps([resource.name, task_command]))

        return JsonResponse({
            'task': map_resource_task(task),
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
