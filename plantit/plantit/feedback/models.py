from django.conf import settings
from django.db import models


class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    used = models.TextField(blank=True, null=True)
    wanted = models.TextField(blank=True, null=True)
    ease = models.TextField(blank=True, null=True)
    features = models.TextField(blank=True, null=True)
