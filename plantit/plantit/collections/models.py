from enum import Enum

from django.conf import settings
from django.db import models
from django_enum_choices.fields import EnumChoiceField


class CollectionRole(Enum):
    read = 'READ'
    write = 'WRITE'


class CollectionAccessPolicy(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owner", on_delete=models.CASCADE)
    guest = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="guest", on_delete=models.CASCADE)
    role = EnumChoiceField(CollectionRole, default=CollectionRole.read)
    path = models.CharField(max_length=250)


# TODO periodic task to test that access is still shared, section in data tab for data shared with you