import json
import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.forms import model_to_dict
from django.utils import timezone
from taggit.managers import TaggableManager

from plantit.targets.models import Target


class Run(models.Model):
    class Meta:
        ordering = ['-created']

    guid = models.CharField(max_length=50, null=False, blank=False)
    tags = TaggableManager()
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(default=timezone.now)
    token = models.CharField(max_length=40)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submission_id = models.CharField(max_length=50, null=True, blank=True)
    job_id = models.CharField(max_length=7, null=True, blank=True)
    job_status = models.CharField(max_length=15, null=True, blank=True)
    job_walltime = models.CharField(max_length=8, null=True, blank=True)
    flow_owner = models.CharField(max_length=280, null=True, blank=True)
    flow_name = models.CharField(max_length=280, null=True, blank=True)
    flow_image_url = models.URLField(null=True, blank=True)
    target = models.ForeignKey(Target, null=True, blank=True, on_delete=models.SET_NULL)
    work_dir = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return json.dumps(model_to_dict(self))

    @property
    def is_sandbox(self):
        return self.target.name is not None and self.target.name == 'Sandbox'

    @property
    def is_success(self):
        return self.job_status == 'SUCCESS' or self.job_status == 'COMPLETED'

    @property
    def is_failure(self):
        return self.job_status == 'FAILURE' or self.job_status == 'FAILED' or self.job_status == 'NODE_FAIL'

    @property
    def is_complete(self):
        return self.is_success or self.is_failure or self.is_cancelled or self.is_timeout

    @property
    def is_cancelled(self):
        return self.job_status == 'REVOKED' or self.job_status == 'CANCELLED'

    @property
    def is_timeout(self):
        return self.job_status == 'TIMEOUT'


class Output(models.Model):
    class Meta:
        ordering = ['-created']

    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True, default='favicon-xyz.png')

    def __str__(self):
        return self.path
