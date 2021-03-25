import json
from itertools import chain

from django.conf import settings
from django.db import models
from django.forms import model_to_dict
from django.utils import timezone
from django_celery_beat.models import PeriodicTask
from taggit.managers import TaggableManager

from plantit.clusters.models import Cluster


class Run(models.Model):
    class Meta:
        ordering = ['-created']

    guid = models.CharField(max_length=50, null=False, blank=False)
    tags = TaggableManager()
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(default=timezone.now)
    completed = models.DateTimeField(null=True, blank=True)
    token = models.CharField(max_length=40)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submission_id = models.CharField(max_length=50, null=True, blank=True)
    job_id = models.CharField(max_length=7, null=True, blank=True)
    job_status = models.CharField(max_length=15, null=True, blank=True)
    job_walltime = models.CharField(max_length=8, null=True, blank=True)
    workflow_owner = models.CharField(max_length=280, null=True, blank=True)
    workflow_name = models.CharField(max_length=280, null=True, blank=True)
    workflow_image_url = models.URLField(null=True, blank=True)
    cluster = models.ForeignKey(Cluster, null=True, blank=True, on_delete=models.SET_NULL)
    work_dir = models.CharField(max_length=100, null=True, blank=True)
    task = models.ForeignKey(PeriodicTask, null=True, blank=True, on_delete=models.CASCADE)

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

    @property
    def is_success(self):
        return self.job_status == 'SUCCESS' or self.job_status == 'COMPLETED'

    @property
    def is_failure(self):
        return self.job_status == 'FAILURE' or self.job_status == 'FAILED' or self.job_status == 'NODE_FAIL'

    @property
    def is_cancelled(self):
        return self.job_status == 'REVOKED' or self.job_status == 'CANCELLED'

    @property
    def is_complete(self):
        return self.is_success or self.is_failure or self.is_cancelled or self.is_timeout

    @property
    def is_timeout(self):
        return self.job_status == 'TIMEOUT'


class DelayedRunTask(PeriodicTask):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE, null=True, blank=True)
    workflow_owner = models.CharField(max_length=280, null=True, blank=True)
    workflow_name = models.CharField(max_length=280, null=True, blank=True)
    eta = models.DateTimeField(null=False, blank=False)


class RepeatingRunTask(PeriodicTask):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE, null=True, blank=True)
    workflow_owner = models.CharField(max_length=280, null=True, blank=True)
    workflow_name = models.CharField(max_length=280, null=True, blank=True)
    eta = models.DateTimeField(null=False, blank=False)
