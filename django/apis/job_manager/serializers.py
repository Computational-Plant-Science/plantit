from plantit.job_manager.job import Job, Status, Task
from rest_framework import serializers

from ..mixins import PinnedSerilizerMethodMixin

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ('state', 'date', 'description' )

class TaskSerializer(serializers.ModelSerializer):
    pk = serializers.IntegerField()

    class Meta:
        model = Task
        fields = ('pk','complete',)

class JobSerializer(serializers.HyperlinkedModelSerializer, PinnedSerilizerMethodMixin):
    status_set = serializers.SerializerMethodField()
    task_set = serializers.SerializerMethodField()
    collection = serializers.StringRelatedField()
    pinned = serializers.SerializerMethodField('pinnedByUser', source='profile_pins')

    class Meta:
        model = Job
        fields = ('pinned', 'pk', 'collection',  'date_created', 'work_dir',
                  'submission_id', 'remote_results_path', 'results_file',
                  'task_set',  'status_set')

    def create(self, validated_data):
        status_data = validated_data.pop('status_set')
        job = Job.objects.create(**validated_data)
        job.save()
        for status in status_data:
            Status.objects.create(job = job, **status_data)
        return job

    def update(self, job, validated_data):
        if 'submission_id' in validated_data.keys():
            job.submission_id = validated_data['submission_id']

        if 'remote_results_path' in validated_data.keys():
            job.remote_results_path = validated_data['remote_results_path']

        status_data = validated_data.get('status_set',None)
        if(status_data):
            for status in status_data:
                Status.objects.create(job = job, **status)

        task_list = validated_data.get('task_set',None)
        if(task_list):
            for task_data in task_list:
                task = job.task_set.get(pk=task_data['pk'])
                if(task.complete == False and task_data['complete'] == True):
                    task.finish()

        job.save()
        return job

    def get_status_set(self, instance):
        status = instance.status_set.all().order_by('-date')
        return StatusSerializer(status, many=True).data

    def get_task_set(self, instance):
        status = instance.task_set.all().order_by('-order_pos')
        return TaskSerializer(status, many=True).data

    def get_queryset(self):
        user = self.request.user
        return Job.objects.filter(user=user)
