import json
from datetime import timedelta

from django.http import JsonResponse, HttpResponseNotFound
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from plantit.runs.ssh import SSH
from plantit.runs.utils import execute_command
from plantit.targets.models import Target, TargetPolicy, TargetTask
from plantit.targets.serializers import TargetSerializer


class TargetsViewSet(viewsets.ModelViewSet):
    queryset = Target.objects.all()
    serializer_class = TargetSerializer
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def __map_task(task):
        return {
            'name': task.name,
            'description': task.description,
            'command': task.command,
            'interval': {
                'every': task.interval.every,
                'period': task.interval.period
            },
            'enabled': task.enabled,
            'last_run': task.last_run_at
        }

    @staticmethod
    def __map_target(target, role):
        tasks = TargetTask.objects.filter(target=target)
        return {
            'name': target.name,
            'role': role.lower(),
            'description': target.description,
            'hostname': target.hostname,
            'pre_commands': target.pre_commands,
            'max_walltime': target.max_walltime,
            'max_mem': target.max_mem,
            'max_cores': target.max_cores,
            'max_processes': target.max_processes,
            'queue': target.queue,
            'project': target.project,
            'workdir': target.workdir,
            'executor': target.executor,
            'disabled': target.disabled,
            'public': target.public,
            'gpu': target.gpu,
            'tasks': [TargetsViewSet.__map_task(task) for task in tasks],
            'logo': target.logo
        }

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
            return JsonResponse(self.__map_target(target, 'none'))

        policy = TargetPolicy.objects.get(user=user, target=target)
        return JsonResponse(self.__map_target(target, policy.role.value))

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
    def get_by_username(self, request):
        user = request.user
        policies = TargetPolicy.objects.filter(user=user)
        targets = [self.__map_target(target, policy.role.value.lower()) for target, policy in
                   zip([policy.target for policy in policies], policies)] + [self.__map_target(target, 'none') for target in
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
        task_delay = request.data['delay']

        schedule, _ = IntervalSchedule.objects.get_or_create(every=int(task_delay), period=IntervalSchedule.SECONDS)
        task, created = TargetTask.objects.get_or_create(
            interval=schedule,
            target=target,
            name=task_name,
            command=task_command,
            description=task_description,
            task='plantit.runs.tasks.run_command',
            args=json.dumps([target.name, task_command]))

        return JsonResponse({
            'task': self.__map_task(task),
            'created': created
        })

    @action(methods=['post'], detail=True)
    def update_task(self, request, name):
        try:
            target = Target.objects.get(name=name)
        except:
            return HttpResponseNotFound()

        task_name = request.POST.get('name', None)
        task_description = request.POST.get('description', None)
        task_command = request.POST.get('command', None)
        task_delay = request.POST.get('delay', None)

        schedule, _ = IntervalSchedule.objects.get_or_create(every=int(task_delay), period=IntervalSchedule.SECONDS)
        try:
            task = TargetTask.objects.get(name=task_name)
        except:
            return HttpResponseNotFound()

        task.interval = schedule
        task.name = task_name,
        task.command = task_command,
        task.description = task_description
        task.task = 'plantit.runs.tasks.run_command',
        task.args = json.dumps([target.name, task_command])
        task.save()

        return JsonResponse({
            'name': task.name,
            'description': task.description,
            'command': task.command,
            'interval': task.interval,
            'enabled': task.enabled,
            'last_run': task.last_run_at
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

    @action(methods=['get'], detail=False)
    def update_singularity_cache_cleaning_schedule(self, request):
        name = request.GET.get('name')
        delay = request.GET.get('delay', None)

        try:
            target = Target.objects.get(name=name)
        except:
            return HttpResponseNotFound()

        if delay is not None:
            target.singularity_cache_clean_delay = timedelta(seconds=int(delay))
        target.singularity_cache_clean_enabled = True

        schedule, _ = IntervalSchedule.objects.get_or_create(every=int(delay), period=IntervalSchedule.SECONDS)
        task = PeriodicTask.objects.get_or_create(
            interval=schedule,
            name=f"Clean singularity cache on {target.name}",
            task='plantit.runs.tasks.clean_singularity_cache',
            args=json.dumps([target.name]))

        target.singularity_cache_clean_task_id = task.id
        target.save()

        return JsonResponse({'enabled': True})

    @action(methods=['get'], detail=False)
    def disable_singularity_cache_cleaning(self, request):
        name = request.GET.get('name')

        try:
            target = Target.objects.get(name=name)
            task = PeriodicTask.objects.get(name=f"Clean singularity cache on {name}")
        except:
            return HttpResponseNotFound()

        task.delete()  # cancel the periodic task
        target.singularity_cache_clean_enabled = False
        target.save()

        return JsonResponse({'enabled': False})
