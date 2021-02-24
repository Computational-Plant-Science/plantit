import json
from typing import List

from django.http import JsonResponse, HttpResponseNotFound
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from plantit.runs.ssh import SSH
from plantit.runs.utils import execute_command
from plantit.targets.models import Target, TargetPolicy, TargetTask, TargetRole
from plantit.targets.serializers import TargetSerializer
from plantit.targets.utils import map_target, map_target_task


class TargetsViewSet(viewsets.ModelViewSet):
    queryset = Target.objects.all()
    serializer_class = TargetSerializer
    permission_classes = (IsAuthenticated,)

    @action(methods=['get'], detail=False)
    def get_all(self, request):
        policies = list(TargetPolicy.objects.all())
        return JsonResponse({'targets': [map_target(policy.target, policy.role, policies) for policy in policies if policy.target.public or policy.user == request.user]})

    @action(methods=['get'], detail=False)
    def get_by_name(self, request):
        name = request.GET.get('name')

        try:
            target = Target.objects.get(name=name)
        except:
            return HttpResponseNotFound()

        user = request.user
        policies = TargetPolicy.objects.filter(user=user)

        if target not in [policy.target for policy in policies]:
            return JsonResponse(map_target(target, TargetRole.none))

        policy = TargetPolicy.objects.get(user=user, target=target)
        return JsonResponse(map_target(target, policy.role, list(policies)))

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
        policies = TargetPolicy.objects.filter(user=user)
        targets = [map_target(target, policy.role, list(policies)) for target, policy in
                   zip([policy.target for policy in policies], policies)] + [map_target(target, TargetRole.none, list(policies)) for target in
                                                                             Target.objects.exclude(targetpolicy__in=policies)]
        return JsonResponse({'targets': targets})

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
