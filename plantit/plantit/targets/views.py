import json
from datetime import timedelta

from django.http import JsonResponse, HttpResponseNotFound, HttpResponse
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from plantit.runs.ssh import SSH
from plantit.runs.utils import execute_command
from plantit.targets.serializers import TargetSerializer
from plantit.targets.models import Target, TargetPolicy


class TargetsViewSet(viewsets.ModelViewSet):
    queryset = Target.objects.all()
    serializer_class = TargetSerializer
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def __convert_target(target, role):
        return {
            'name': target.name,
            'role': role.value.lower(),
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
            'singularity_cache_clean_enabled': target.singularity_cache_clean_enabled,
            'singularity_cache_clean_delay': target.singularity_cache_clean_delay,
            'workdir_clean_delay': target.workdir_clean_delay,
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
            return HttpResponseNotFound()

        policy = TargetPolicy.objects.get(user=user, target=target)
        return JsonResponse(self.__convert_target(target, policy.role))

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
        targets = [policy.target for policy in policies]

        return JsonResponse({'targets': [{
            'name': target.name,
            'role': policy.role.value.lower(),
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
            'gpu': target.gpu,
            'singularity_cache_clean_enabled': target.singularity_cache_clean_enabled,
            'singularity_cache_clean_delay': target.singularity_cache_clean_delay,
            'workdir_clean_delay': target.workdir_clean_delay
        } for target, policy in zip(targets, policies)]})

    @action(methods=['get'], detail=False)
    def schedule_singularity_cache_cleaning(self, request):
        name = request.GET.get('name')
        delay = request.GET.get('delay', None)

        try:
            target = Target.objects.get(name=name)
        except:
            return HttpResponseNotFound()

        if delay is not None:
            target.singularity_cache_clean_delay = timedelta(seconds=int(delay))
        target.singularity_cache_clean_enabled = True
        target.save()

        schedule, _ = IntervalSchedule.objects.get_or_create(every=int(delay), period=IntervalSchedule.SECONDS)
        PeriodicTask.objects.create(
            interval=schedule,
            name=f"Clean singularity cache on {target.name}",
            task='plantit.runs.tasks.clean_singularity_cache',
            args=json.dumps([target.name]))

        return JsonResponse({'enabled': True})

    @action(methods=['get'], detail=False)
    def unschedule_singularity_cache_cleaning(self, request):
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
