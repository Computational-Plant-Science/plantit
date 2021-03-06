import json
from enum import Enum

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django_enum_choices.fields import EnumChoiceField


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
    public: bool = models.BooleanField(default=False)
    logo: str = models.URLField(null=True, blank=True)
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


@receiver(post_save, sender=Target)
def schedule_default_tasks(sender, instance, created, **kwargs):
    if not created:
        return

    every_minute, _ = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.MINUTES)
    healthcheck_task = TargetTask.objects.create(
        target=instance,
        interval=every_minute,
        name=f"{instance.name} healthcheck",
        task='plantit.runs.tasks.run_command',
        args=json.dumps([instance.name, 'pwd']))


class TargetRole(Enum):
    own = 'OWN'
    run = 'USE'
    none = 'NONE'


class TargetPolicy(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    target = models.ForeignKey(Target, null=True, blank=True, on_delete=models.CASCADE)
    role = EnumChoiceField(TargetRole, default=TargetRole.run)


class TargetTask(PeriodicTask):
    target = models.ForeignKey(Target, on_delete=models.CASCADE)
    command = models.CharField(max_length=250, null=False, blank=False)


class TargetAccessRequest(models.Model):
    created = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    target = models.ForeignKey(Target, null=True, blank=True, on_delete=models.CASCADE)
    granted: bool = models.BooleanField(default=False)
