import json
import uuid

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
from plantit.clusters.models import Cluster, ClusterAccessPolicy, ClusterTask, ClusterRole, ClusterAccessRequest
from plantit.clusters.serializers import ClusterSerializer
from plantit.clusters.utils import map_cluster, map_cluster_task


class ClustersViewSet(viewsets.ModelViewSet):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer
    permission_classes = (IsAuthenticated,)

    @action(methods=['get'], detail=False)
    def get_all(self, request):
        clusters = list(Cluster.objects.filter(public=True))
        return JsonResponse({'clusters': [map_cluster(cluster) for cluster in clusters]})

    @action(methods=['get'], detail=False)
    def grant_access(self, request):
        cluster_name = request.GET.get('name', None)
        user_name = request.GET.get('user', None)

        if cluster_name is None or user_name is None:
            return HttpResponseNotFound()

        try:
            cluster = Cluster.objects.get(name=cluster_name)
            user = User.objects.get(username=user_name)
        except:
            return HttpResponseNotFound()

        policy, created = ClusterAccessPolicy.objects.get_or_create(user=user, cluster=cluster, role=ClusterRole.run)
        access_request = ClusterAccessRequest.objects.get(user=user, cluster=cluster)
        access_request.delete()

        notification = TargetPolicyNotification.objects.create(
            guid=str(uuid.uuid4()),
            user=user,
            created=timezone.now(),
            policy=policy,
            message=f"You were granted access to {policy.cluster.name}")
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
        cluster_name = request.GET.get('name', None)
        user_name = request.GET.get('user', None)

        if cluster_name is None or user_name is None:
            return HttpResponseNotFound()

        try:
            cluster = Cluster.objects.get(name=cluster_name)
            user = User.objects.get(username=user_name)
            policy = ClusterAccessPolicy.objects.get(user=user, cluster=cluster)
        except:
            return HttpResponseNotFound()

        notification = TargetPolicyNotification.objects.create(
            guid=str(uuid.uuid4()),
            user=user,
            created=timezone.now(),
            policy=policy,
            message=f"Your access to {policy.cluster.name} was revoked")
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
        cluster_name = request.GET.get('name', None)
        if cluster_name is None:
            return HttpResponseNotFound()

        try:
            cluster = Cluster.objects.get(name=cluster_name)
        except:
            return HttpResponseNotFound()

        _, created = ClusterAccessRequest.objects.get_or_create(user=request.user, cluster=cluster)
        return JsonResponse({
            'created': created
        })

    @action(methods=['get'], detail=False)
    def toggle_public(self, request):
        cluster_name = request.GET.get('name', None)
        if cluster_name is None:
            return HttpResponseNotFound()

        try:
            cluster = Cluster.objects.get(name=cluster_name)
        except:
            return HttpResponseNotFound()

        cluster.public = not cluster.public
        cluster.save()

        return JsonResponse({'public': cluster.public})

    @action(methods=['get'], detail=False)
    def get_by_name(self, request):
        cluster_name = request.GET.get('name')

        try:
            cluster = Cluster.objects.get(name=cluster_name)
        except:
            return HttpResponseNotFound()

        user = request.user
        policies = ClusterAccessPolicy.objects.filter(cluster=cluster)

        try:
            access_requests = ClusterAccessRequest.objects.filter(cluster=cluster)
        except:
            access_requests = None

        if cluster not in [policy.cluster for policy in policies]:
            return JsonResponse(map_cluster(cluster, ClusterRole.none, None, access_requests))

        try:
            role = ClusterAccessPolicy.objects.get(user=user, cluster=cluster).role
        except:
            role = ClusterRole.none
        return JsonResponse(map_cluster(cluster, role, list(policies), access_requests))

    @action(methods=['get'], detail=False)
    def status(self, request):
        name = request.GET.get('name')

        try:
            cluster = Cluster.objects.get(name=name)
        except:
            return HttpResponseNotFound()

        try:
            ssh = SSH(cluster.hostname, cluster.port, cluster.username)
            with ssh:
                lines = execute_command(
                    ssh_client=ssh,
                    pre_command=':',
                    command=f"pwd",
                    directory=cluster.workdir)
                print(lines)
                return JsonResponse({'healthy': True})
        except:
            return JsonResponse({'healthy': False})

    @action(methods=['get'], detail=False)
    def get_users(self, request):
        name = request.GET.get('name')

        try:
            cluster = Cluster.objects.get(name=name)
        except:
            return HttpResponseNotFound()

        policies = ClusterAccessPolicy.objects.filter(cluster=cluster)
        JsonResponse({'policies': list(policies)})

    @action(methods=['get'], detail=False)
    def get_by_username(self, request):
        user = request.user
        policies = ClusterAccessPolicy.objects.filter(user=user, role__in=[ClusterRole.own, ClusterRole.run])
        clusters = [map_cluster(cluster, policy.role, list(policies)) for cluster, policy in zip([policy.cluster for policy in policies], policies) if
                    policy.role != ClusterRole.none]
        return JsonResponse({'clusters': clusters})

    @action(methods=['post'], detail=False)
    def create_task(self, request):
        try:
            cluster_name = request.data['cluster']
            cluster = Cluster.objects.get(name=cluster_name)
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
        task, created = ClusterTask.objects.get_or_create(
            crontab=schedule,
            cluster=cluster,
            name=task_name,
            command=task_command,
            description=task_description,
            task='plantit.runs.tasks.run_command',
            args=json.dumps([cluster.name, task_command]))

        return JsonResponse({
            'task': map_cluster_task(task),
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
