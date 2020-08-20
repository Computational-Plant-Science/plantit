from django.db import models
from django.utils.translation import gettext_lazy


class Target(models.Model):

    name = models.CharField(max_length=20,
                            help_text="Human-readable name of cluster.")

    description = models.TextField(blank=True,
                                   help_text="Human-readable description of cluster.")

    workdir = models.CharField(max_length=250,
                               help_text="Where (full path) to put folders for pipeline analysis jobs on the cluster.")

    username = models.CharField(max_length=100,
                                help_text="ssh username")

    port = models.PositiveIntegerField(default=22,
                                       help_text="ssh port")

    hostname = models.CharField(max_length=250,
                                help_text="ssh hostname")

    pre_commands = models.TextField(help_text="Commands to run before starting jobs.",
                                    blank=True,
                                    null=True,
                                    default=None)

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


