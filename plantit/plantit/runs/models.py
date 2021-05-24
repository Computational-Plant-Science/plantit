import json
from itertools import chain

from django.conf import settings
from django.db import models
from django.forms import model_to_dict
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from django_celery_beat.models import PeriodicTask
from taggit.managers import TaggableManager

from plantit.resources.models import Resource


class Run(models.Model):
    class Meta:
        ordering = ['-created']

    guid = models.CharField(max_length=50, null=False, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, null=True, blank=True, on_delete=models.SET_NULL)
    workdir = models.CharField(max_length=100, null=True, blank=True)
    token = models.CharField(max_length=40)
    tags = TaggableManager()
    submission_id = models.CharField(max_length=50, null=True, blank=True)
    job_id = models.CharField(max_length=7, null=True, blank=True)
    job_status = models.CharField(max_length=15, null=True, blank=True)
    job_requested_walltime = models.CharField(max_length=8, null=True, blank=True)
    job_elapsed_walltime = models.CharField(max_length=8, null=True, blank=True)
    workflow_owner = models.CharField(max_length=280, null=True, blank=True)
    workflow_name = models.CharField(max_length=280, null=True, blank=True)
    workflow_image_url = models.URLField(null=True, blank=True)
    task = models.ForeignKey(PeriodicTask, null=True, blank=True, on_delete=models.CASCADE)
    results = ArrayField(models.CharField(max_length=250), blank=True, null=True)
    previews_loaded = models.BooleanField(default=False)
    cleaned_up = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(default=timezone.now)
    completed = models.DateTimeField(null=True, blank=True)

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
        return self.resource.name is not None and self.resource.name == 'Sandbox'

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
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=True, blank=True)
    workflow_owner = models.CharField(max_length=280, null=True, blank=True)
    workflow_name = models.CharField(max_length=280, null=True, blank=True)
    eta = models.DateTimeField(null=False, blank=False)


class RepeatingRunTask(PeriodicTask):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=True, blank=True)
    workflow_owner = models.CharField(max_length=280, null=True, blank=True)
    workflow_name = models.CharField(max_length=280, null=True, blank=True)
    eta = models.DateTimeField(null=False, blank=False)
