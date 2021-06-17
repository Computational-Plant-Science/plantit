from django.conf import settings
from django.db import models


class Workflow(models.Model):
    class Meta:
        unique_together = ('repo_owner', 'repo_name')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    repo_owner = models.CharField(max_length=280, null=True, blank=True)
    repo_name = models.CharField(max_length=280, null=True, blank=True)
    public = models.BooleanField(default=False)
