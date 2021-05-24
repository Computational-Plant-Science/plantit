from rest_framework import serializers

from plantit.resources.models import Resource


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ('name', 'description', 'hostname', 'pre_commands', 'max_walltime', 'max_mem', 'max_cores', 'max_processes', 'queue', 'project', 'workdir', 'executor', 'disabled', 'gpu')