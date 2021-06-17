import json
from enum import Enum
from itertools import chain

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django_enum_choices.fields import EnumChoiceField

from plantit.agents.models import Agent


class DatasetRole(Enum):
    read = 'READ'
    write = 'WRITE'


class DatasetAccessPolicy(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owner", on_delete=models.CASCADE)
    guest = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="guest", on_delete=models.CASCADE)
    role = EnumChoiceField(DatasetRole, default=DatasetRole.read)
    path = models.CharField(max_length=250)


# TODO periodic task to test that access is still shared, section in data tab for data shared with you


class DatasetSession(models.Model):
    guid = models.CharField(max_length=50, null=False, blank=False, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    path = models.CharField(max_length=250)
    agent = models.ForeignKey(Agent, null=True, blank=True, on_delete=models.SET_NULL)
    workdir = models.CharField(max_length=100, null=True, blank=True)
    token = models.CharField(max_length=40)
    modified = ArrayField(models.CharField(max_length=250), blank=True, null=True)
    save_task_id = models.CharField(max_length=50, null=True, blank=True)
    channel_name = models.CharField(max_length=200, null=True, blank=True)
    opening = models.BooleanField(default=True, null=False, blank=False)

    def __str__(self):
        opts = self._meta
        data = {}
        for f in chain(opts.concrete_fields, opts.private_fields):
            data[f.name] = f.value_from_object(self)
        for f in opts.many_to_many:
            data[f.name] = [i.id for i in f.value_from_object(self)]
        return json.dumps(data)

    @property
    def is_sandbox(self):
        return self.agent.name is not None and self.agent.name == 'Sandbox'
