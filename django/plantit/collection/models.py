from __future__ import absolute_import, unicode_literals
from celery import shared_task

import json
import os.path
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from model_utils.managers import InheritanceManager

from .mixins import CastableModelMixin, CastableQuerySetMixin

from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

from .. import file_manager
from plantit.file_manager.filesystems import registrar
import plantit.file_manager.permissions as permissions

@shared_task
def generate_thumbnail(sample_pk):
    """
        Generate the thumbnail image for a sample

        Args:
            sample_pk: pk of the sample
    """
    sample = Sample.objects.get(pk = sample_pk)
    base_file_path = sample.collection.base_file_path
    storage_type = sample.collection.storage_type
    folder = file_manager.open(storage_type,base_file_path)
    file = folder.open(sample.path)

    sample.thumbnail.save(sample.name,file)

class MetaData(models.Model):
    """
        Basic Metadata class.

        Attributes:
            key (str): Metadata key
            value (str): Metadata value
    """
    key = models.CharField(max_length=50)
    objects = InheritanceManager()

class Tag(models.Model):
    """
        All tags are available to all collections and should be used to broadly
        describe the contents of a collection, allowing it to be easily
        found via a site-wide search. For example, a collection that
        is related to maze would get a "maze" tag, allowing it to show up
        when users are looking for analysis related to maze.

        Attributes:
            tag (str): tag
            description (str): tag description
    """
    tag = models.CharField(max_length=50)
    description = models.CharField(max_length=250)

class CustomQuerySet(CastableQuerySetMixin, models.QuerySet):
    pass

class Collection(models.Model, CastableModelMixin):
    """
        Collections are items that are analyzed togeather.
        Typically representing one experiment or treatment.

        Attributes:
            name (str): the name of the collection
            description (str): text description and/or notes
            user (ForeignKey): primary user for the collection
            tag (ManyToMany): :class:`workflows.models.Tag`s associated with the
                collection
            metadata (ManyToMany): User configurable metadata. Must extend
                type :class:`workflows.models.AbstractMetaData`
    """
    objects = CustomQuerySet.as_manager()
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True,null=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    metadata = models.ManyToManyField(MetaData,blank=True)
    storage_type = models.CharField(max_length=25)
    base_file_path = models.CharField(max_length=250)
    tags = models.ManyToManyField(Tag,blank=True)

    def __str__(self):
        return self.name

    def to_json(self):
        """
            Create a json representation of the collection

            returns (String): json string
        """
        collection = {}
        if self.storage_type == "local":
            for sample in self.sample_set.all():
                collection[sample.name] = {
                            "storage": "local",
                            "path": sample.path
                        }
        elif self.storage_type == "irods":
            for sample in self.sample_set.all():
                irods_storage = registrar.list["irods"]
                collection[sample.name] = {
                            "storage": "irods",
                            "path": os.path.join(self.base_file_path,
                                                 sample.path),
                            "hostname": irods_storage.hostname,
                            "password": irods_storage.password,
                            "port": irods_storage.port,
                            "zone": irods_storage.zone,
                            "username": irods_storage.username
                        }
        return json.dumps(collection)

    def get_absolute_url(self):
        """
            Return the canonical URL for an object. Defines a default
            url for FormViews that use this model.

            see https://docs.djangoproject.com/en/2.0/ref/models/instances/#django.db.models.Model.get_absolute_url for
            details.
        """
        return "/collection/%d/details/"%(self.pk,)

    def add_sample(self,name,path,**kwargs):
        s = self.sample_set.create(path=path,name=name,**kwargs)
        print(s.pk)
        generate_thumbnail.delay(s.pk)

class Sample(models.Model):
    """
        Represents one experimental sample. I.E. The unit of information that
        is analyzed by the workflow.

        Attributes:
            collection (:class:`Collection`): the collection this sample
                belongs to
            path (String): the path to the file relative to collection's
                base file path.
    """
    objects = CustomQuerySet.as_manager()
    name = models.CharField(max_length=250,null=False,blank=False)
    path = models.CharField(max_length=250,null=False,blank=False)
    collection = models.ForeignKey(Collection,on_delete=models.CASCADE)
    thumbnail = ProcessedImageField(upload_to='static/collections/thumbnails',
                                       processors=[ResizeToFill(100, 100)],
                                       format='JPEG',
                                       options={'quality': 60},
                                       blank=True)

    def __str__(self):
        return self.name

    def get(self,user,base_file_path):
        storage = permissions.open_folder(self.collection.storage_type,
                                          self.collection.base_file_path,
                                          self.collection.user)

        return storage.open(self.path)
