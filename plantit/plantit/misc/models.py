from django.db import models
from django.utils import timezone


class NewsUpdate(models.Model):
    created = models.DateTimeField(default=timezone.now)
    content = models.TextField(blank=True)


class MaintenanceWindow(models.Model):
    start = models.DateTimeField(null=False, blank=False)
    end = models.DateTimeField(null=False, blank=False)
