from rest_framework import serializers

from plantit.clusters.models import Cluster


class ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cluster
        fields = ('name', 'description', 'hostname', 'pre_commands', 'max_walltime', 'max_mem', 'max_cores', 'max_processes', 'queue', 'project', 'workdir', 'executor', 'disabled', 'gpu')