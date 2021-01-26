from rest_framework import serializers
from datetime import datetime

from plantit.runs.models import Run, Status


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ('state', 'date', 'description')


class RunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Run
        fields = ('pk', 'cluster', 'flow_owner', 'flow_name',
                  'created', 'timeout', 'started', 'work_dir', 'identifier',
                  'remote_results_path')

    def create(self, validated_data):
        status_data = validated_data.pop('status_set')
        run = Run.objects.create(**validated_data)
        run.save()
        for _ in status_data:
            Status.objects.create(run=run, **status_data)
        return run

    def update(self, run, validated_data):
        print(validated_data)
        if 'identifier' in validated_data.keys():
            run.identifier = validated_data['identifier']

        if 'remote_results_path' in validated_data.keys():
            run.remote_results_path = validated_data['remote_results_path']

        status_data = validated_data.get('status_set', None)
        if status_data:
            for status in status_data:
                status['date'] = datetime.now()
                Status.objects.create(run=run, **status)

        run.save()
        return run
