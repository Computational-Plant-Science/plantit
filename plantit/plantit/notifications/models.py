from django.conf import settings
from django.db import models
from django.utils import timezone

from plantit.stores.models import DirectoryPolicy
from plantit.targets.models import TargetPolicy


class Notification(models.Model):
    guid = models.CharField(max_length=50, null=False, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now)
    message = models.CharField(max_length=1000, null=True, blank=True)
    read: bool = models.BooleanField(default=False)

    class Meta:
        abstract = True


class DirectoryPolicyNotification(Notification):
    policy = models.ForeignKey(DirectoryPolicy, on_delete=models.CASCADE)


class TargetPolicyNotification(Notification):
    policy = models.ForeignKey(TargetPolicy, on_delete=models.CASCADE)
