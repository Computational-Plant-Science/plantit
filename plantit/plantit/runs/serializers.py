from rest_framework import serializers
from datetime import datetime

from plantit.runs.models import Run


class RunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Run
        fields = ('pk', 'cluster', 'flow_owner', 'flow_name',
                  'created', 'walltime', 'timeout', 'work_dir', 'submission_task_id', 'job_id',
                  'remote_results_path')

    def create(self, validated_data):
        run = Run.objects.create(**validated_data)
        run.save()
        return run

    def update(self, run, validated_data):
        print(validated_data)
        if 'submission_task_id' in validated_data.keys():
            run.submission_task_id = validated_data['submission_task_id']

        if 'remote_results_path' in validated_data.keys():
            run.remote_results_path = validated_data['remote_results_path']

        run.save()
        return run
