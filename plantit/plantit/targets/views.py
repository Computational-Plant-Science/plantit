from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from plantit.targets.serializers import TargetSerializer
from plantit.targets.models import Target, TargetPolicy


class TargetsViewSet(viewsets.ModelViewSet):
    queryset = Target.objects.all()
    serializer_class = TargetSerializer
    permission_classes = (IsAuthenticated,)

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
            'gpu': target.gpu
        } for target, policy in zip(targets, policies)]})


