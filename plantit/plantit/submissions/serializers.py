from rest_framework import serializers

from plantit.submissions.models import Submission


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ('pk', 'guid', 'cluster', 'flow_owner', 'flow_name',
                  'created', 'work_dir', 'job_id', 'job_status')

    def create(self, validated_data):
        submission = Submission.objects.create(**validated_data)
        submission.save()
        return submission

    def update(self, submission, validated_data):
        submission.save()
        return submission
