import json
from itertools import chain

from django.conf import settings
from django.db import models
from django.utils import timezone

from plantit.clusters.models import Cluster


class Session(models.Model):
    guid = models.CharField(max_length=50, null=False, blank=False, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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
