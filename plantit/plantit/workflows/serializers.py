from rest_framework import serializers

from plantit.workflows.models import Workflow


class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = ('repo_owner', 'repo_name', 'public')
