import json

from django.conf import settings
from django.db import models
from django.forms import model_to_dict
from django.utils import timezone
from taggit.managers import TaggableManager

from plantit.targets.models import Target


class Run(models.Model):
    class Meta:
        ordering = ['-created']

    tags = TaggableManager()
    created = models.DateTimeField(default=timezone.now)
    walltime = models.IntegerField(default=600, null=False, blank=False)
    timeout = models.IntegerField(default=600, null=False, blank=False)
    token = models.CharField(max_length=40)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submission_task_id = models.CharField(max_length=36, null=False, blank=False)
    completion_task_id = models.CharField(max_length=36, null=True, blank=True)
    job_id = models.CharField(max_length=7, null=True, blank=True)
    flow_owner = models.CharField(max_length=280, null=True, blank=True)
    flow_name = models.CharField(max_length=280, null=True, blank=True)
    target = models.ForeignKey(Target, null=True, blank=True, on_delete=models.SET_NULL)
    work_dir = models.CharField(max_length=100, null=True, blank=True, default=timezone.now().strftime('%s') + "/")
    remote_results_path = models.CharField(max_length=100, null=True, blank=True, default=None)

    def __str__(self):
        return json.dumps(model_to_dict(self))

    @property
    def is_sandbox(self):
        return self.target.name is not None and self.target.name == 'Sandbox'


class Output(models.Model):
    class Meta:
        ordering = ['-created']

    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True, default='favicon-xyz.png')

    def __str__(self):
        return self.path
