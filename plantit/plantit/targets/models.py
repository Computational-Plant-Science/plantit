from datetime import timedelta

from django.db import models
from django.utils.translation import gettext_lazy


class Target(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    workdir = models.CharField(max_length=250)
    username = models.CharField(max_length=100)
    port = models.PositiveIntegerField(default=22)
    hostname = models.CharField(max_length=250)
    pre_commands = models.TextField(blank=True, null=True, default=None)
    max_walltime = models.PositiveIntegerField(blank=True, null=True, default=10)
    max_mem = models.IntegerField(blank=True, null=True, default=5)
    max_cores = models.IntegerField(blank=True, null=True, default=1)
    max_processes = models.IntegerField(blank=True, null=True, default=1)
    queue = models.CharField(max_length=250, null=True, blank=True)
    project = models.CharField(max_length=250, null=True, blank=True)
    header_skip = models.CharField(max_length=1000, null=True, blank=True)
    gpu = models.BooleanField(null=False, default=False)
    gpu_queue = models.CharField(max_length=250, null=True, blank=True)
    disabled: bool = models.BooleanField(default=False)
    cleanup_delay = models.DurationField(null=False, blank=False, default=timedelta(days=7))
    no_nested = models.BooleanField(default=False)  # https://github.com/Computational-Plant-Science/plantit/issues/98

    class Executor(models.TextChoices):
        LOCAL = 'local', gettext_lazy('Local')
        SLURM = 'slurm', gettext_lazy('SLURM')
        PBS = 'pbs', gettext_lazy('PBS')

    executor = models.CharField(
        max_length=10,
        choices=Executor.choices,
        default=Executor.LOCAL)

    def __str__(self):
        return self.name
