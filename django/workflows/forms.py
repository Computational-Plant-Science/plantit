from django import forms
from file_manager.fields import FileUploadField

from job_manager.job import Job
from job_manager.remote import Cluster

class CollectionFileForm(forms.Form):
    files = forms.ModelMultipleChoiceField(required=False,queryset=None)
    file = FileUploadField(required=False)

    def __init__(self, choices = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['files'].queryset = choices

class CreateJob(forms.ModelForm):
    cluster = forms.ModelChoiceField(queryset=Cluster.objects.all())
    class Meta:
        model = Job
        exclude = ('date_created',)
