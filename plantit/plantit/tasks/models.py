import json
from itertools import chain
from typing import TypedDict, List

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy
from django_celery_beat.models import PeriodicTask
from enum import Enum
from taggit.managers import TaggableManager

from plantit.agents.models import Agent, AgentScheduler
from plantit.miappe.models import Investigation, Study


class TaskStatus(models.TextChoices):
    CREATED = 'created', gettext_lazy('Created')
    RUNNING = 'running', gettext_lazy('Running')
    SUCCESS = 'success', gettext_lazy('Success')
    FAILURE = 'failure', gettext_lazy('Failure')
    TIMEOUT = 'timeout', gettext_lazy('Timeout')
    CANCELED = 'canceled', gettext_lazy('Canceled')


# from https://steelkiwi.com/blog/practical-application-singleton-design-pattern/
class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


# for computing statistics; incremented every time a new task is created
class TaskCounter(SingletonModel):
    count = models.PositiveBigIntegerField(default=0, null=False, blank=False)


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
    project = models.ForeignKey(Investigation, null=True, blank=True, on_delete=models.SET_NULL)
    inputs_detected = models.IntegerField(null=True, blank=True, default=0)
    inputs_downloaded = models.IntegerField(null=True, blank=True, default=0)
    inputs_submitted = models.IntegerField(null=True, blank=True, default=0)
    inputs_completed = models.IntegerField(null=True, blank=True, default=0)
    study = models.ForeignKey(Study, null=True, blank=True, on_delete=models.SET_NULL)
    workflow = models.JSONField(null=False, blank=False)
    workflow_owner = models.CharField(max_length=280, null=False, blank=False)
    workflow_name = models.CharField(max_length=280, null=False, blank=False)
    workflow_branch = models.CharField(max_length=280, null=False, blank=False)
    workflow_image_url = models.URLField(null=True, blank=True)
    status = models.CharField(max_length=8, choices=TaskStatus.choices, default=TaskStatus.CREATED)
    results = ArrayField(models.CharField(max_length=250), blank=True, null=True)
    results_retrieved = models.BooleanField(default=False)
    results_transferred = models.IntegerField(null=True, blank=True, default=0)
    previews_loaded = models.BooleanField(default=False)
    cleaned_up = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(default=timezone.now)
    completed = models.DateTimeField(null=True, blank=True)
    celery_task_id = models.CharField(max_length=50, null=True, blank=True)
    transferred = models.BooleanField(default=False)
    transfer_path = models.CharField(max_length=250, null=True, blank=True)
    due_time = models.DateTimeField(null=True, blank=True)
    cleanup_time = models.DateTimeField(null=True, blank=True)
    delayed_id = models.CharField(max_length=250, null=True, blank=True)
    repeating_id = models.CharField(max_length=250, null=True, blank=True)

    @property
    def is_success(self):
        return self.status == TaskStatus.SUCCESS or self.job_status == 'SUCCESS' or self.job_status == 'COMPLETED'

    @property
    def is_failure(self):
        return self.status == TaskStatus.FAILURE or self.job_status == 'FAILURE' or self.job_status == 'FAILED' or self.job_status == 'NODE_FAIL' or self.status == 'FAILURE'

    @property
    def is_timeout(self):
        return self.status == TaskStatus.TIMEOUT or self.job_status == 'TIMEOUT'

    @property
    def is_cancelled(self):
        return self.status == TaskStatus.CANCELED or self.job_status == 'REVOKED' or self.job_status == 'CANCELLED' or self.job_status == 'CANCELED'

    @property
    def is_complete(self):
        return self.is_success or self.is_failure or self.is_timeout or self.is_cancelled

    def __str__(self):
        opts = self._meta
        data = {}
        for f in chain(opts.concrete_fields, opts.private_fields):
            data[f.name] = f.value_from_object(self)
        for f in opts.many_to_many:
            data[f.name] = [i.id for i in f.value_from_object(self)]
        return json.dumps(data)

    # jobqueue stuff
    job_id = models.CharField(max_length=50, null=True, blank=True)
    job_status = models.CharField(max_length=15, null=True, blank=True)
    job_requested_walltime = models.CharField(max_length=8, null=True, blank=True)
    job_consumed_walltime = models.CharField(max_length=8, null=True, blank=True)


# scheduled tasks

class DelayedTask(PeriodicTask):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    resource = models.ForeignKey(Agent, on_delete=models.CASCADE, null=True, blank=True)
    workflow_owner = models.CharField(max_length=280, null=True, blank=True)
    workflow_name = models.CharField(max_length=280, null=True, blank=True)
    workflow_branch = models.CharField(max_length=280, null=True, blank=True)
    workflow_image_url = models.URLField(null=True, blank=True)
    eta = models.DateTimeField(null=False, blank=False)


class RepeatingTask(PeriodicTask):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    resource = models.ForeignKey(Agent, on_delete=models.CASCADE, null=True, blank=True)
    workflow_owner = models.CharField(max_length=280, null=True, blank=True)
    workflow_name = models.CharField(max_length=280, null=True, blank=True)
    workflow_branch = models.CharField(max_length=280, null=True, blank=True)
    workflow_image_url = models.URLField(null=True, blank=True)
    eta = models.DateTimeField(null=False, blank=False)


# task options

class BindMount(TypedDict):
    host_path: str
    container_path: str


class Parameter(TypedDict):
    key: str
    value: str


class EnvironmentVariable(TypedDict):
    key: str
    value: str


class Input(TypedDict, total=False):
    kind: str
    path: str
    patterns: List[str]


class InputKind(str, Enum):
    FILE = 'file'
    FILES = 'files'
    DIRECTORY = 'directory'


class FileChecksum(TypedDict):
    file: str
    checksum: str


class TaskOptions(TypedDict, total=False):
    workdir: str
    image: str
    command: str
    input: Input
    output: dict
    parameters: List[Parameter]
    env: List[EnvironmentVariable]
    bind_mounts: List[BindMount]
    checksums: List[FileChecksum]
    log_file: str
    jobqueue: dict
    no_cache: bool
    gpu: bool
