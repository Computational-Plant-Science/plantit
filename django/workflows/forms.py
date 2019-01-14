from django import forms
from django.forms.widgets import NumberInput
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from job_manager.remote import Cluster

from .models import Result

class CreateJob(forms.Form):
    cluster = forms.ModelChoiceField(queryset=Cluster.objects.all())
    cluster.group = "Job Settings"
