from django.db import models
from django.utils.translation import gettext_lazy


class Target(models.Model):

    name = models.CharField(max_length=20,
                            help_text="Human-readable name.")

    description = models.TextField(blank=True,
                                   help_text="Human-readable description.")

    workdir = models.CharField(max_length=250,
                               help_text="Working directory.")

    username = models.CharField(max_length=100,
                                help_text="SSH username.")

    port = models.PositiveIntegerField(default=22,
                                       help_text="SSH port.")

    hostname = models.CharField(max_length=250,
                                help_text="SSH hostname.")

    pre_commands = models.TextField(help_text="Commands to execute before starting a run.",
                                    blank=True,
                                    null=True,
                                    default=None)

    max_walltime = models.PositiveIntegerField(help_text="Maximum walltime for runs (minutes).", blank=True, null=True, default=10)

    max_mem = models.PositiveIntegerField(help_text="Maximum memory for runs (GB)", blank=True, null=True, default=10)

    class Executor(models.TextChoices):
        LOCAL = 'LO', gettext_lazy('Local')
        SLURM = 'SL', gettext_lazy('SLURM')
        PBS = 'PB', gettext_lazy('PBS')

    executor = models.CharField(
        max_length=2,
        choices=Executor.choices,
        default=Executor.LOCAL)

    def __str__(self):
        return self.name


