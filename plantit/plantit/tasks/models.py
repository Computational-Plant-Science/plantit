import json
from enum import Enum
from itertools import chain
from typing import TypedDict, List

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy
from django_celery_beat.models import PeriodicTask
from taggit.managers import TaggableManager

from plantit.agents.models import Agent
from plantit.miappe.models import Investigation, Study


class TaskStatus(models.TextChoices):
    CREATED = 'created', gettext_lazy('Created')
    RUNNING = 'running', gettext_lazy('Running')
    COMPLETED = 'completed', gettext_lazy('Completed')
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

    guid = models.CharField(max_length=50, null=False, blank=False, unique=True)
    name = models.CharField(max_length=250, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, null=True, blank=True, on_delete=models.SET_NULL)
    workdir = models.CharField(max_length=100, null=True, blank=True)
    token = models.CharField(max_length=40)
    tags = TaggableManager()
    inputs_detected = models.IntegerField(null=True, blank=True, default=0)
    inputs_downloaded = models.IntegerField(null=True, blank=True, default=0)
    inputs_submitted = models.IntegerField(null=True, blank=True, default=0)
    inputs_completed = models.IntegerField(null=True, blank=True, default=0)
    project = models.ForeignKey(Investigation, null=True, blank=True, on_delete=models.SET_NULL)
    study = models.ForeignKey(Study, null=True, blank=True, on_delete=models.SET_NULL)
    workflow = models.JSONField(null=False, blank=False)
    workflow_owner = models.CharField(max_length=280, null=False, blank=False)
    workflow_name = models.CharField(max_length=280, null=False, blank=False)
    workflow_branch = models.CharField(max_length=280, null=False, blank=False)
    workflow_image_url = models.URLField(null=True, blank=True)
    status = models.CharField(max_length=9, choices=TaskStatus.choices, default=TaskStatus.CREATED)
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

    def __str__(self):
        opts = self._meta
        data = {}
        for f in chain(opts.concrete_fields, opts.private_fields):
            data[f.name] = f.value_from_object(self)
        for f in opts.many_to_many:
            data[f.name] = [i.id for i in f.value_from_object(self)]
        return json.dumps(data)

    # SLURM #

    SLURM_RUNNING_STATES = [
        'CF', 'CONFIGURING',
        'PD', 'PENDING',
        'R', 'RUNNING',
        'RD', 'RESV_DEL_HOLD',
        'RF', 'REQUEUE_FED',
        'RH', 'REQUEUE_HOLD',
        'RQ', 'REQUEUED',
        'RS', 'RESIZING',
        'SI', 'SIGNALING',
        'SO', 'STAGE_OUT',
        'S', 'SUSPENDED',
        'ST', 'STOPPED'
    ]

    SLURM_SUCCESS_STATES = [
        'CG', 'COMPLETING',
        'CD', 'COMPLETED',
    ]

    SLURM_CANCELLED_STATES = [
        'CA', 'CANCELLED',
        'RV', 'REVOKED'
    ]

    SLURM_TIMEOUT_STATES = [
        'DL', 'DEADLINE',
        'TO', 'TIMEOUT'
    ]

    SLURM_FAILURE_STATES = [
        'BF', 'BOOT_FAIL',
        'F', 'FAILED',
        'NF', 'NODE_FAIL',
        'OOM', 'OUT_OF_MEMORY',
        'PR', 'PREEMPTED',
    ]

    # inbound data transfer
    pull_id = models.CharField(max_length=50, null=True, blank=True)
    pull_status = models.CharField(max_length=15, null=True, blank=True)

    # main job (user workflow)
    job_id = models.CharField(max_length=50, null=True, blank=True)
    job_status = models.CharField(max_length=15, null=True, blank=True)
    job_requested_walltime = models.CharField(max_length=8, null=True, blank=True)
    job_consumed_walltime = models.CharField(max_length=8, null=True, blank=True)

    # outbound data transfer
    push_id = models.CharField(max_length=50, null=True, blank=True)
    push_status = models.CharField(max_length=15, null=True, blank=True)

    # State props #

    @property
    def is_success(self):
        return (self.pull_status in self.SLURM_SUCCESS_STATES
                and self.job_status in self.SLURM_SUCCESS_STATES
                and self.push_status in self.SLURM_SUCCESS_STATES) \
               or (self.status == TaskStatus.COMPLETED or
                   self.status == 'success')  # legacy (TODO: may no longer be necessary?)

    @property
    def is_failure(self):
        return self.pull_status in self.SLURM_FAILURE_STATES \
               or self.job_status in self.SLURM_FAILURE_STATES \
               or self.push_status in self.SLURM_FAILURE_STATES \
               or self.status == TaskStatus.FAILURE

    @property
    def is_timeout(self):
        return self.pull_status in self.SLURM_TIMEOUT_STATES \
               or self.job_status in self.SLURM_TIMEOUT_STATES \
               or self.push_status in self.SLURM_TIMEOUT_STATES \
               or self.status == TaskStatus.TIMEOUT

    @property
    def is_cancelled(self):
        return self.pull_status in self.SLURM_CANCELLED_STATES \
               or self.job_status in self.SLURM_CANCELLED_STATES \
               or self.push_status in self.SLURM_CANCELLED_STATES \
               or self.status == TaskStatus.CANCELED

    @property
    def is_complete(self):
        return self.is_success or self.is_failure or self.is_timeout or self.is_cancelled


# Scheduled Tasks #

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


# Task Options #

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
    gpus: bool
    shell: str
