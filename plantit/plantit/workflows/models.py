from django.conf import settings
from django.db import models
from taggit.managers import TaggableManager


class Workflow(models.Model):
    class Meta:
        ordering = ['-created']

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    repo_owner = models.CharField(max_length=280, null=True, blank=True)
    repo_name = models.CharField(max_length=280, null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    tags = TaggableManager()
