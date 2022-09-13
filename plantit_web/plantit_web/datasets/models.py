import json
from enum import Enum
from itertools import chain

from django.conf import settings
from django.db import models
from django_enum_choices.fields import EnumChoiceField

from plantit_web.agents.models import Agent


class DatasetRole(Enum):
    read = 'READ'
    write = 'WRITE'


class DatasetAccessPolicy(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owner", on_delete=models.CASCADE)
    guest = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="guest", on_delete=models.CASCADE)
    role = EnumChoiceField(DatasetRole, default=DatasetRole.read)
    path = models.CharField(max_length=250)


# TODO periodic task to test that access is still shared, section in data tab for data shared with you
