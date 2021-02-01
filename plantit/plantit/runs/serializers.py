from rest_framework import serializers

from plantit.runs.models import Run


class RunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Run
        fields = ('pk', 'guid', 'cluster', 'flow_owner', 'flow_name',
                  'created', 'work_dir', 'job_id', 'job_status')

    def create(self, validated_data):
        run = Run.objects.create(**validated_data)
        run.save()
        return run

    def update(self, run, validated_data):
        run.save()
        return run
