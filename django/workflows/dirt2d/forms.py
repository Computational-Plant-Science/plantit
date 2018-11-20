from django import forms

from job_manager.remote import Cluster

from .models import Result

class CreateJob(forms.Form):
    cluster = forms.ModelChoiceField(queryset=Cluster.objects.all())
    cluster.group = "Job Settings"

    class Meta:
        model = Result
        exclude = ['circle ratio','x pixel','y pixel','xScale','yScale',
            'computation time','Skeleton Vertices']

    def __init__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)

        for key,value in self.Meta.model.attributes.items():
            if key in self.Meta.exclude:
                continue

            self.fields[key] = forms.BooleanField(required=False)
            self.initial[key] = value['initial']
            self.fields[key].group = value['group']
            self.fields[key].label = value['name']

    def get_cleaned_attributes(self):
        attributes = {}
        for attribute in self.Meta.model.attributes.keys():
            if attribute in self.Meta.exclude:
                continue

            attributes[attribute] = self.cleaned_data[attribute]

        return attributes
