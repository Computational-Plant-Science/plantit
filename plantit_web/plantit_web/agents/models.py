from datetime import timedelta
from enum import Enum

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy


class AgentScheduler(models.TextChoices):
    SLURM = 'slurm', gettext_lazy('SLURM')
    PBS = 'pbs', gettext_lazy('PBS')


class AgentAuthentication(models.TextChoices):
    PASSWORD = 'password', gettext_lazy('Password')
    KEY = 'key', gettext_lazy('Key')


class Agent(models.Model):
    name = models.CharField(max_length=50, unique=True)
    guid = models.CharField(max_length=50, null=False, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    workdir = models.CharField(max_length=250)
    username = models.CharField(max_length=100)
    port = models.PositiveIntegerField(default=22)
    hostname = models.CharField(max_length=250)
    pre_commands = models.TextField(blank=True, null=True, default=None)
    max_time = models.DurationField(blank=False, null=False, default=timedelta(hours=1))
    max_walltime = models.PositiveIntegerField(blank=True, null=True, default=10)
    max_mem = models.IntegerField(blank=True, null=True, default=5)
    max_cores = models.IntegerField(blank=True, null=True, default=1)
    max_tasks = models.IntegerField(blank=True, null=True, default=20)
    max_processes = models.IntegerField(blank=True, null=True, default=1)
    max_nodes = models.IntegerField(blank=True, null=True, default=1)
    orchestrator_queue = models.CharField(max_length=250, null=True, blank=True)
    queue = models.CharField(max_length=250, null=True, blank=True)
    project = models.CharField(max_length=250, null=True, blank=True)
    header_skip = models.CharField(max_length=1000, null=True, blank=True)
    gpus = models.IntegerField(null=False, default=0)
    disabled = models.BooleanField(default=False)
    public = models.BooleanField(default=False)
    logo = models.URLField(null=True, blank=True)
    job_array = models.BooleanField(default=False)  # https://github.com/Computational-Plant-Science/plantit/issues/98
    launcher = models.BooleanField(default=False)   # https://github.com/TACC/launcher
    scheduler = models.CharField(max_length=10, choices=AgentScheduler.choices, default=AgentScheduler.SLURM)
    is_healthy = models.BooleanField(default=True, null=True, blank=True)
    users_authorized = models.ManyToManyField(User, related_name='agents_authorized', null=True, blank=True)

    def __str__(self):
        return self.name


class AgentRole(str, Enum):
    admin = 'admin'
    guest = 'guest'
    none = 'none'


class AgentAccessPolicy(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, null=True, blank=True, on_delete=models.CASCADE)


class AgentUsagePolicy(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, null=True, blank=True, on_delete=models.CASCADE)
    # TODO: how to define usage policy?
    # first as number of successful submissions
    # later as CPU hours? total runtime? normalized by resources used?
    # https://github.com/Computational-Plant-Science/plantit/issues/236
