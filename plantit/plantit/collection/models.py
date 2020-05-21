from __future__ import absolute_import, unicode_literals

import os.path

import json
from celery import shared_task
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

import plantit.stores.permissions as permissions
from .mixins import CastableModelMixin, CastableQuerySetMixin
from .. import stores


@shared_task
def generate_thumbnail(sample_pk):
    """
        Generate the thumbnail image for a sample. This function runs
        in a :mod:`~plantit.celery` task and is automatically called by
        :func:`Collection.add_sample` when a
        sample is added to a collection.

        Sample type is automatically detected and the correct thumbnail
        code is run for the sample type. If the sample format is not supported,
        :attr:`Sample.thumbnail_supported` is set to false and
        :attr:`Sample.thumbnail` is left `null`

        If a thumbnail is generated, :py:attr:`Sample.thumbnail_supported` is
        set to true and :attr:`Sample.thumbnail` is set to the thumbnail image.
        See :attr:`Sample.thumbnail` for more information.

        Note:
            Currently only supports creating thumbnails of images
            (jpeg, jpg, png, tiff).

        Args:
            sample_pk (int): pk of the sample
    """
    sample = Sample.objects.get(pk = sample_pk)
    base_file_path = sample.collection.base_file_path
    storage_type = sample.collection.storage_type

    _, file_extension = os.path.splitext(sample.path)

    if(file_extension.lower() in ['.jpeg', '.jpg', '.png', '.tiff']):
        #Sample type is already a supported image type
        #Simply open the image and let the thumbnail field format the image
        folder = stores.open(storage_type, base_file_path)
        file = folder.open(sample.path)
        sample.thumbnail.save(sample.name,file)
        sample.thumbnail_supported = True
        sample.save()
    else:
        #No other supported file types, show a default image
        sample.thumbnail_supported = False
        sample.save()
        pass

class CustomQuerySet(CastableQuerySetMixin, models.QuerySet):
    '''
        Add support to cast an object to its final class.
        See :class:`CastableQuerySetMixin` for details.
    '''
    pass

class Collection(models.Model, CastableModelMixin):
    """
        Collections are a set of samples hat are analyzed together by the
        same Plant IT workflow. Typically representing one experiment or
        treatment.

        Attributes:
            name (str): the name of the collection
            description (str): text description and/or notes
            user (ForeignKey): primary user for the collection
            storage_type (string): The name of the storage system the samples
                are saved on. It must be a key in
                :attr:`..file_manager.filesystems.Registrar.list`
            base_file_path (str): Sample paths are relative to this path on the
                file system.
            metadata (:class:`JSONField`): Metadata for the collection.
    """
    objects = CustomQuerySet.as_manager()
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True,null=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    storage_type = models.CharField(max_length=25)
    base_file_path = models.CharField(max_length=250)
    metadata = JSONField(default=list,blank=True)

    def __str__(self):
        return self.name

    def to_json(self):
        """
            Create a json representation of the collection

            returns (String): json string
        """
        collection = {
            "name": self.name,
            "storage_type": self.storage_type,
            "base_file_path": self.base_file_path,
            "sample_set": {}
        }

        for sample in self.sample_set.all():
            collection["sample_set"][sample.name] = {
                        "storage": self.storage_type,
                        "path": os.path.join(self.base_file_path,
                                             sample.path),
                    }

        return json.dumps(collection)

    def add_sample(self,name,path,**kwargs):
        '''
            Create a new :class:`Sample` and add it to this collection.
            :func:`generate_thumbnail` is automatically called when the sample
            is added.

            Args:
                name (string): Name of the sample
                path (string): Path to the sample. Relative to the collection's
                    :attr:`~Collection.base_file_path` and
                    :attr:`~Collection.storage_type`.
        '''
        s = self.sample_set.create(path=path,name=name,**kwargs)
        generate_thumbnail.delay(s.pk)

class Sample(models.Model):
    """
        Represents one experimental sample. I.E. The unit of information that
        is analyzed by the workflow.

        Sample objects only contain a link to the path to the files
        within the sample. :mod:`plantit.file_manager` is used to access
        the files.

        Attributes:
            collection (:class:`Collection`): the collection this sample
                belongs to
            path (String): the path to the file relative to collection's
                base file path.
            name (String): the name of the sample
            thumbnail_supported (bool): Thumbnails are supported for this sample
                type. This is set to false by generate_thumbnail() if
                the sample format is  not supported by generate_thumbnail
            thumbnail (ProcessedImageField): url to the thumbnail. See
                django-imagekit for details on saving a new thumbnail. This
                is set to null if 1) generate_thumbnail was not called or
                has not finished running, or 2) thubnail_supported = False
    """
    objects = CustomQuerySet.as_manager()
    name = models.CharField(max_length=250,null=False,blank=False)
    path = models.CharField(max_length=250,null=False,blank=False)
    collection = models.ForeignKey(Collection,on_delete=models.CASCADE)
    thumbnail_supported = models.BooleanField(default=True)
    thumbnail = ProcessedImageField(upload_to='collections/thumbnails',
                                       processors=[ResizeToFill(100, 100)],
                                       format='JPEG',
                                       options={'quality': 60},
                                       blank=True)
    metadata = JSONField(default=list, blank=True)

    def __str__(self):
        return self.name

    def get(self):
        """
            Get the sample file/folder.

            Returns:
                A file like object containing the sample data.
        """
        storage = permissions.open_folder(self.collection.storage_type,
                                          self.collection.base_file_path,
                                          self.collection.user)

        return storage.open(self.path)
