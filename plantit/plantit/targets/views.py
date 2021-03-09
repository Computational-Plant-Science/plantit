import json
import uuid
from typing import List

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from plantit.notifications.models import TargetPolicyNotification
from plantit.runs.ssh import SSH
from plantit.runs.utils import execute_command
from plantit.targets.models import Target, TargetPolicy, TargetTask, TargetRole, TargetAccessRequest
from plantit.targets.serializers import TargetSerializer
from plantit.targets.utils import map_target, map_target_task


class TargetsViewSet(viewsets.ModelViewSet):
    queryset = Target.objects.all()
    serializer_class = TargetSerializer
    permission_classes = (IsAuthenticated,)

    @action(methods=['get'], detail=False)
    def get_all(self, request):
        targets = list(Target.objects.filter(public=True))
        return JsonResponse({'servers': [map_target(target) for target in targets]})

    @action(methods=['get'], detail=False)
    def grant_access(self, request):
        target_name = request.GET.get('name', None)
        user_name = request.GET.get('user', None)

        if target_name is None or user_name is None:
            return HttpResponseNotFound()

        try:
            target = Target.objects.get(name=target_name)
            user = User.objects.get(username=user_name)
        except:
            return HttpResponseNotFound()

        policy, created = TargetPolicy.objects.get_or_create(user=user, target=target, role=TargetRole.run)
        access_request = TargetAccessRequest.objects.get(user=user, target=target)
        access_request.delete()

        notification = TargetPolicyNotification.objects.create(
            guid=str(uuid.uuid4()),
            user=user,
            created=timezone.now(),
            policy=policy,
            message=f"You were granted access to {policy.target.name}")
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
        target_name = request.GET.get('name', None)
        user_name = request.GET.get('user', None)

        if target_name is None or user_name is None:
            return HttpResponseNotFound()

        try:
            target = Target.objects.get(name=target_name)
            user = User.objects.get(username=user_name)
            policy = TargetPolicy.objects.get(user=user, target=target)
        except:
            return HttpResponseNotFound()

        notification = TargetPolicyNotification.objects.create(
            guid=str(uuid.uuid4()),
            user=user,
            created=timezone.now(),
            policy=policy,
            message=f"Your access to {policy.target.name} was revoked")
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
        target_name = request.GET.get('name', None)
        if target_name is None:
            return HttpResponseNotFound()

        try:
            target = Target.objects.get(name=target_name)
        except:
            return HttpResponseNotFound()

        _, created = TargetAccessRequest.objects.get_or_create(user=request.user, target=target)
        return JsonResponse({
            'created': created
        })

    @action(methods=['get'], detail=False)
    def toggle_public(self, request):
        target_name = request.GET.get('name', None)
        if target_name is None:
            return HttpResponseNotFound()

        try:
            target = Target.objects.get(name=target_name)
        except:
            return HttpResponseNotFound()

        target.public = not target.public
        target.save()

        return JsonResponse({'public': target.public})

    @action(methods=['get'], detail=False)
    def get_by_name(self, request):
        target_name = request.GET.get('name')

        try:
            target = Target.objects.get(name=target_name)
        except:
            return HttpResponseNotFound()

        user = request.user
        policies = TargetPolicy.objects.filter(target=target)

        try:
            access_requests = TargetAccessRequest.objects.filter(target=target)
        except:
            access_requests = None

        if target not in [policy.target for policy in policies]:
            return JsonResponse(map_target(target, TargetRole.none, None, access_requests))

        try:
            role = TargetPolicy.objects.get(user=user, target=target).role
        except:
            role = TargetRole.none
        return JsonResponse(map_target(target, role, list(policies), access_requests))

    @action(methods=['get'], detail=False)
    def status(self, request):
        name = request.GET.get('name')

        try:
            target = Target.objects.get(name=name)
        except:
            return HttpResponseNotFound()

        try:
            ssh = SSH(target.hostname, target.port, target.username)
            with ssh:
                lines = execute_command(
                    ssh_client=ssh,
                    pre_command=':',
                    command=f"pwd",
                    directory=target.workdir)
                print(lines)
                return JsonResponse({'healthy': True})
        except:
            return JsonResponse({'healthy': False})

    @action(methods=['get'], detail=False)
    def get_users(self, request):
        name = request.GET.get('name')

        try:
            target = Target.objects.get(name=name)
        except:
            return HttpResponseNotFound()

        policies = TargetPolicy.objects.filter(target=target)
        JsonResponse({'policies': list(policies)})

    @action(methods=['get'], detail=False)
    def get_by_username(self, request):
        user = request.user
        policies = TargetPolicy.objects.filter(user=user, role__in=[TargetRole.own, TargetRole.run])
        targets = [map_target(target, policy.role, list(policies)) for target, policy in zip([policy.target for policy in policies], policies) if
                   policy.role != TargetRole.none]  # + [map_target(target, TargetRole.none, list(policies)) for target in Target.objects.exclude(targetpolicy__in=policies)]
        return JsonResponse({'servers': targets})

    @action(methods=['post'], detail=False)
    def create_task(self, request):
        try:
            target_name = request.data['target']
            target = Target.objects.get(name=target_name)
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
        # schedule, _ = IntervalSchedule.objects.get_or_create(every=int(task_delay), period=IntervalSchedule.SECONDS)
        task, created = TargetTask.objects.get_or_create(
            crontab=schedule,
            target=target,
            name=task_name,
            command=task_command,
            description=task_description,
            task='plantit.runs.tasks.run_command',
            args=json.dumps([target.name, task_command]))

        return JsonResponse({
            'task': map_target_task(task),
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
