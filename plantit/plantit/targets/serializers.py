from rest_framework import serializers

from plantit.targets.models import Target


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ('name', 'description', 'hostname', 'pre_commands', 'max_walltime', 'max_mem', 'max_cores', 'max_processes', 'default_queue', 'default_project', 'workdir', 'executor')