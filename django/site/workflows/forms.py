from django import forms
from django.forms.widgets import NumberInput
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from job_manager.remote import Cluster

def create_field(type,params,**kwargs):
    field = type(initial=params['initial'],**kwargs)
    field.label = params['name']
    return field

def field_factory(params,group):
    type = params['type']
    if type == 'bool':
        field = create_field(forms.BooleanField,params,required=False)
    if type == 'float':
        field = create_field(forms.FloatField,params)
    if type == 'int':
        field = create_field(forms.IntegerField,params)
    field.group = group
    return field

def parse_group(group):
    if 'params' in group.keys():
        for param in group['params']:
            field = field_factory(param,group['name'])
            id = param['id']
            yield id,field

    if 'groups' in group.keys():
        for g in group['groups']:
            yield from parse_group(g)

class CreateJob(forms.Form):
    cluster = forms.ModelChoiceField(queryset=Cluster.objects.all())
    cluster.group = "Job Settings"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for group in self.parameters:
            for id,field in parse_group(group):
                self.fields[id] = field

    def get_grouped_data(self):
        grouped = {}

        for group in self.parameters:
            grouped[group['id']] = self.__group_parameters__(group)

        print(grouped)
        return grouped

    def __group_parameters__(self,group):
        dict = {}

        if 'params' in group.keys():
            p = {}
            for param in group['params']:
                p[param['id']] = self.cleaned_data[param['id']]
            dict['params'] = p
        if 'groups' in group.keys():
            dict['groups'] = {}
            for g in group['groups']:
                dict['groups'][g['id']] = self.__group_parameters__(g)

        return dict
