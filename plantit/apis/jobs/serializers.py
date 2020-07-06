from rest_framework import serializers
from datetime import datetime

from plantit.jobs.models.job import Job
from plantit.jobs.models.status import Status
from ..mixins import PinnedSerilizerMethodMixin


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ('state', 'date', 'description')


class JobSerializer(serializers.ModelSerializer, PinnedSerilizerMethodMixin):
    status_set = StatusSerializer(many=True)
    collection = serializers.StringRelatedField()
    cluster = serializers.SerializerMethodField()
    pinned = serializers.SerializerMethodField('pinnedByUser', source='profile_pins')
    workflow_name = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ('pk', 'pinned', 'collection', 'pipeline',
                  'cluster', 'workflow_name',
                  'created', 'work_dir',
                  'remote_results_path', 'status_set')

    def create(self, validated_data):
        status_data = validated_data.pop('status_set')
        job = Job.objects.create(**validated_data)
        job.save()
        for _ in status_data:
            Status.objects.create(job=job, **status_data)
        return job

    def update(self, job, validated_data):
        print(validated_data)
        if 'submission_id' in validated_data.keys():
            job.submission_id = validated_data['submission_id']

        if 'remote_results_path' in validated_data.keys():
            job.remote_results_path = validated_data['remote_results_path']

        status_data = validated_data.get('status_set', None)
        if status_data:
            for status in status_data:
                status['date'] = datetime.now()
                Status.objects.create(job=job, **status)

        job.save()
        return job
