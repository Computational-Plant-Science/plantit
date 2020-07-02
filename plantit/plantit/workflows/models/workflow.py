from django.conf import settings
from django.db import models
from django.utils import timezone

from taggit.managers import TaggableManager


class Workflow(models.Model):
    class Meta:
        ordering = ['-created']

    created = models.DateTimeField(default=timezone.now())
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    commands = models.TextField(null=False, blank=False)
    repository = models.CharField(max_length=250, null=True, blank=True)
    requirements = TaggableManager()
