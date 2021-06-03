import json
from itertools import chain

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy
from django_celery_beat.models import PeriodicTask
from taggit.managers import TaggableManager

from plantit.agents.models import Agent


class TaskStatus(models.TextChoices):
    CREATED = 'created', gettext_lazy('Created')
    RUNNING = 'running', gettext_lazy('Running')
    SUCCESS = 'success', gettext_lazy('Success')
    FAILURE = 'failure', gettext_lazy('Failure')
    TIMEOUT = 'timeout', gettext_lazy('Timeout')
    CANCELED = 'canceled', gettext_lazy('Canceled')


class Task(models.Model):
    class Meta:
        ordering = ['-created']

    guid = models.CharField(max_length=50, null=False, blank=False)
    name = models.CharField(max_length=250, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, null=True, blank=True, on_delete=models.SET_NULL)
    workdir = models.CharField(max_length=100, null=True, blank=True)
    token = models.CharField(max_length=40)
    tags = TaggableManager()
    workflow_owner = models.CharField(max_length=280, null=True, blank=True)
    workflow_name = models.CharField(max_length=280, null=True, blank=True)
    workflow_image_url = models.URLField(null=True, blank=True)
    results = ArrayField(models.CharField(max_length=250), blank=True, null=True)
    previews_loaded = models.BooleanField(default=False)
    cleaned_up = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(default=timezone.now)
    completed = models.DateTimeField(null=True, blank=True)
    celery_task_id = models.CharField(max_length=50, null=True, blank=True)

    status = models.CharField(
        max_length=8,
        choices=TaskStatus.choices,
        default=TaskStatus.CREATED)

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

    @property
    def is_success(self):
        return self.status == TaskStatus.SUCCESS

    @property
    def is_failure(self):
        return self.status == TaskStatus.FAILURE

    @property
    def is_timeout(self):
        return self.status == TaskStatus.TIMEOUT

    @property
    def is_cancelled(self):
        return self.status == TaskStatus.CANCELED

    @property
    def is_complete(self):
        return self.is_success or self.is_failure or self.is_timeout or self.is_cancelled


class JobQueueTask(Task):
    job_id = models.CharField(max_length=7, null=True, blank=True)
    job_status = models.CharField(max_length=15, null=True, blank=True)
    job_requested_walltime = models.CharField(max_length=8, null=True, blank=True)
    job_elapsed_walltime = models.CharField(max_length=8, null=True, blank=True)

    @property
    def is_sandbox(self):
        return self.agent.name is not None and self.agent.name == 'Sandbox'

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


class DelayedTask(PeriodicTask):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    resource = models.ForeignKey(Agent, on_delete=models.CASCADE, null=True, blank=True)
    workflow_owner = models.CharField(max_length=280, null=True, blank=True)
    workflow_name = models.CharField(max_length=280, null=True, blank=True)
    eta = models.DateTimeField(null=False, blank=False)


class RepeatingTask(PeriodicTask):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    resource = models.ForeignKey(Agent, on_delete=models.CASCADE, null=True, blank=True)
    workflow_owner = models.CharField(max_length=280, null=True, blank=True)
    workflow_name = models.CharField(max_length=280, null=True, blank=True)
    eta = models.DateTimeField(null=False, blank=False)
