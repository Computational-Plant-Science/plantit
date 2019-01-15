from django import forms
from django.forms.widgets import NumberInput
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from job_manager.remote import Cluster

from workflows.forms import CreateJob

from .models import Dirt2DResult

class ThresholdWidget(NumberInput):
    """
        Provides a ajax file browser
    """
    class Media:
        js = ("workflows/dirt2d/js/load_image.js",)
        css = {
            'all' : ('workflows/dirt2d/css/load_image.css',)
        }

    def __init__(self, thresholds=(0.5,1,10,25), *args, **kwargs):
        super(forms.widgets.Widget, self).__init__(*args, **kwargs)
        self.attrs = { 'thresholds': thresholds }

    def render(self, name, value, attrs=None, renderer=None):
        template_name = 'workflows/dirt2d/thresholds.html'

        return mark_safe(render_to_string(template_name,self.attrs))

class CreateJob(CreateJob):
    threshold = forms.FloatField(widget=ThresholdWidget)
    threshold.group = "Job Settings"

    class Meta:
        model = Dirt2DResult
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
