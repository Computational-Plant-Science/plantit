from dagster import DagsterType
from django.db import models
from encrypted_model_fields.fields import EncryptedCharField


class Cluster(models.Model):
    name = models.CharField(max_length=20,
                            help_text="Human-readable name of cluster.")
    description = models.TextField(blank=True,
                                   help_text="Human-readable description of cluster.")
    workdir = models.CharField(max_length=250,
                               help_text="Where (full path) to put folders for pipeline analysis jobs on the cluster.")
    username = models.CharField(max_length=100,
                                help_text="ssh username")
    password = EncryptedCharField(max_length=100, blank=True, null=True, default=None,
                                  help_text="ssh password. Leave blank for public-key auth. See README for setup.")
    port = models.PositiveIntegerField(default=22,
                                       help_text="ssh port")
    hostname = models.CharField(max_length=250,
                                help_text="ssh hostname")
    pre_commands = models.TextField(help_text="Commands to run before starting jobs.")
    submit_commands = models.TextField(default="clusterside submit",
                                       help_text="Commands to run to submit a job.")

    def __str__(self):
        return self.name


