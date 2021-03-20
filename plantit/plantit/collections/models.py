import json
from enum import Enum
from itertools import chain

from django.conf import settings
from django.db import models
from django_enum_choices.fields import EnumChoiceField

from plantit.clusters.models import Cluster


class CollectionRole(Enum):
    read = 'READ'
    write = 'WRITE'


class CollectionAccessPolicy(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owner", on_delete=models.CASCADE)
    guest = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="guest", on_delete=models.CASCADE)
    role = EnumChoiceField(CollectionRole, default=CollectionRole.read)
    path = models.CharField(max_length=250)


# TODO periodic task to test that access is still shared, section in data tab for data shared with you


class CollectionSession(models.Model):
    guid = models.CharField(max_length=50, null=False, blank=False, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    path = models.CharField(max_length=250)
    cluster = models.ForeignKey(Cluster, null=True, blank=True, on_delete=models.SET_NULL)
    workdir = models.CharField(max_length=100, null=True, blank=True)
    token = models.CharField(max_length=40)

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
        return self.cluster.name is not None and self.cluster.name == 'Sandbox'
