from django.db import models
from django.utils import timezone


class NewsUpdate(models.Model):
    created = models.DateTimeField(default=timezone.now)
    content = models.TextField(blank=True)
