from django.db import models
from django.utils import timezone


class NewsUpdate(models.Model):
    created = models.DateTimeField(default=timezone.now)
    content = models.TextField(blank=True)


class MaintenanceWindow(models.Model):
    start = models.DateTimeField(null=False, blank=False)
    end = models.DateTimeField(null=False, blank=False)


class FeaturedWorkflow(models.Model):
    owner = models.CharField(max_length=250, blank=False, null=False)
    name = models.CharField(max_length=250, blank=False, null=False)
    branch = models.CharField(max_length=250, blank=False, null=False)
