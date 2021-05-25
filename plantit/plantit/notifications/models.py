from django.conf import settings
from django.db import models
from django.utils import timezone

from plantit.datasets.models import DatasetAccessPolicy
from plantit.agents.models import AgentAccessPolicy


class Notification(models.Model):
    guid = models.CharField(max_length=50, null=False, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    message = models.CharField(max_length=1000, null=True, blank=True)
    read: bool = models.BooleanField(default=False)

    class Meta:
        abstract = True


class DirectoryPolicyNotification(Notification):
    policy = models.ForeignKey(DatasetAccessPolicy, on_delete=models.CASCADE)


class TargetPolicyNotification(Notification):
    policy = models.ForeignKey(AgentAccessPolicy, on_delete=models.CASCADE)
