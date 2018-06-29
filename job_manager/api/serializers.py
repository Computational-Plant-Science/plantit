from job_manager.models import Job, Status
from rest_framework import serializers


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ('state', 'date', 'description' )

class JobSerializer(serializers.HyperlinkedModelSerializer):
    status_set = StatusSerializer(many=True)

    class Meta:
        model = Job
        fields = ('pk', 'date_created', 'status_set', 'submission_id')

    def create(self, validated_data):
        status_data = validated_data.pop('status_set')
        job = Job.objects.create(**validated_data)
        job.save()
        for status in status_data:
            Status.objects.create(job = job, **status_data)
        return job

    def update(self, job, validated_data):
        if(validated_data['submission_id']):
            job.submission_id = validated_data['submission_id']
        status_data = validated_data.pop('status_set')
        for status in status_data:
            Status.objects.create(job = job, **status)
        job.save()
        return job

    #
    # def get_current_status(self, job):
    #     serializer = StatusSerializer(instance=job.current_status())
    #     return serializer.data
    #
    # def validate_current_status(self, value):
    #     print(value)
    #
    # def update(self, instance, validated_data):
    #     print(validated_data)
    #     return instance
