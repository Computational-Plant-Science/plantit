from django import forms

from job_manager.remote import Cluster
from job_manager.job import Job

class CreateJob(forms.ModelForm):
    cluster = forms.ModelChoiceField(queryset=Cluster.objects.all())
    class Meta:
        model = Job
        exclude = ('date_created','collection','user','submission_id','auth_token','work_dir')
