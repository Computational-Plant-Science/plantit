from rest_framework import serializers

from plantit.agents.models import Agent


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ('name', 'guid', 'description', 'hostname', 'pre_commands', 'max_walltime', 'max_mem', 'max_cores', 'max_processes', 'queue', 'project', 'workdir', 'executor', 'disabled', 'gpu')