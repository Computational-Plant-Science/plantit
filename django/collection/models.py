from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from workflows.models import Tag
from model_utils.managers import InheritanceManager
from .mixins import CastableModelMixin, CastableQuerySetMixin

class MetaData(models.Model):
    """
        Basic Metadata class.

        Attributes:
            key (str): Metadata key
            value (str): Metadata value
    """
    key = models.CharField(max_length=50)
    objects = InheritanceManager()

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

        Child classes must add the following attributes:
            + files (ForeignKey): Files within the collection. Must extend
                type :class:`job_manager.models.AbstractFile`

    """
    objects = CustomQuerySet.as_manager()
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True,null=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag,blank=True)
    metadata = models.ManyToManyField(MetaData,blank=True)
    storage_type = models.CharField(max_length=25)
    base_file_path = models.CharField(max_length=250)

    def __str__(self):
        return self.name

    def add_file(self,file):
        raise NotImplementedError

    def get_absolute_url(self):
        """
            Return the canonical URL for an object. Defines a default
            url for FormViews that use this model.

            see https://docs.djangoproject.com/en/2.0/ref/models/instances/#django.db.models.Model.get_absolute_url for
            details.
        """
        return "/collection/%d/details/"%(self.pk,)
