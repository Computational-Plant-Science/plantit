from enum import Enum

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django_enum_choices.fields import EnumChoiceField


class DirectoryRole(Enum):
    read = 'READ'
    write = 'WRITE'


class DirectoryPolicy(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owner", on_delete=models.CASCADE)
    guest = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="guest", on_delete=models.CASCADE)
    role = EnumChoiceField(DirectoryRole, default=DirectoryRole.read)
    path = models.CharField(max_length=250)


# TODO periodic task to test that access is still shared, section in data tab for data shared with you