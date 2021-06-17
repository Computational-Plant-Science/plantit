from rest_framework import serializers

from plantit.tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('pk', 'guid', 'cluster', 'flow_owner', 'flow_name',
                  'created', 'work_dir', 'job_id', 'job_status')

    def create(self, validated_data):
        task = Task.objects.create(**validated_data)
        task.save()
        return task

    def update(self, task, validated_data):
        task.save()
        return task
