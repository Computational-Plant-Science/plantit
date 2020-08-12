from __future__ import absolute_import, unicode_literals

from os.path import join

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from ..stores.irodsstore import IRODS, IRODSOptions


class Dataset(models.Model):
    name = models.CharField(max_length=250, unique=True)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    storage_type = models.CharField(max_length=25)
    base_file_path = models.CharField(max_length=250)
    public = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'user'], name='unique_dataset')
        ]


class DatasetMetadatum(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    key = models.CharField(max_length=250, unique=True)
    value = models.CharField(max_length=250)


def __irods():
    return IRODS(IRODSOptions(settings.IRODS_HOST,
                              int(
                                  settings.IRODS_PORT),
                              settings.IRODS_USERNAME,
                              settings.IRODS_PASSWORD,
                              settings.IRODS_ZONE))


@receiver(post_save, sender=Dataset)
def create_irods_collection(sender, instance, created, **kwargs):
    if created:
        path = join(settings.IRODS_BASEPATH, instance.user.username, instance.name)
        irods = __irods()
        irods.create_collection(path)
        instance.base_file_path = path
        instance.save()


@receiver(post_delete, sender=Dataset)
def delete_irods_collection(sender, instance, using, **kwargs):
    irods = __irods()
    irods.delete_collection(instance.base_file_path)


post_save.connect(create_irods_collection, sender=Dataset)
post_delete.connect(delete_irods_collection, sender=Dataset)