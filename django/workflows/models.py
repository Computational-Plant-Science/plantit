from django.db import models
from django.contrib.auth.models import User
from job_manager.models import Job

"""
    A workflow consists of a collection of files, details about the files
    (metadata), and a collection of tasks that are run to analze the files.
    Typically, the tasks are the same across all collections in the same
    workflow.

    Modules inside :module:`workflows.models` that are specific to each workflow
    are prefixed with "Abstract", indicating they need to be extended
    independentially by each workflow.

    See :module:`workflows.dirt2d.models` for a working example
"""

class AbstractDefaults(models.Model):
    """
        Workflow defaults should be saved using this class by extending it and
        adding fields for each default.

        The class  guarantees only 1 defaults object can exist.

        Example:
            models.py:
            .. code-block:: python
                from workflows.models import AbstractDefaults
                from django.db import models

                class Defaults(AbstractDefaults):
                    parameters = models.TextField(null=True,blank=True)

            view.py:
            .. code-block:: python
                from .models import Defaults

                ...
                    defaults = Deafults.load()
                    print(defaults.paramaters)
                ...
    """
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(AbstractDefaults, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        """
            Load defaults

            Returns:
                (object): defaults
        """
        return cls.objects.get(pk=1)


class AbstractMetaData(models.Model):
    """ Metadata is specific to a workflow and should be
        exteded by each workflow.
        Basic Metadata class.

        Attributes:
            key (str): Metadata key
            value (str): Metadata value
    """
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=250)

    class Meta:
        abstract = True

class Tag(models.Model):
    """
        All tags are available to all workflows and should be used to broadly
        describe the contents of a workflow collection, allowing it to be easily
        found via a site-wide search. For example, a workflow collection that
        is related to maze would get a "maze" tag, allowing it to show up
        when users are looking for analysis realted to maze.

        Tags should not be exteded by individual workflows.

        Attributes:
            tag (str): tag
            description (str): tag description
    """
    tag = models.CharField(max_length=50)
    description = models.CharField(max_length=250)


class AbstractCollection(models.Model):
    """
        Collections are items that are analyzed togeather.
        Typically representing one experiment or treatment.

        Attributes:
            name (str): the name of the collection
            description (str): text description and/or notes
            user (ForeignKey): primary user for the collection
            tag (ManyToMany): :class:`workflows.models.Tag`s associated with the
                collection
            job (ForeignKey): the :class:`job_manager.models.Job` submitted to
                analzye the collection

        Child classes must add the following attributes:
            + files (ForeignKey): Files within the collection. Must extend
                type :class:`job_manager.models.AbstractFile`
            + metadata (ManyToMany): User configurable metadata. Must extend
                type :class:`workflows.models.AbstractMetaData`
    """
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True,null=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag,blank=True)
    job = models.ForeignKey(Job,null=True,blank=True,on_delete=models.SET_NULL)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """
            Return the canonical URL for an object.
            see https://docs.djangoproject.com/en/2.0/ref/models/instances/#django.db.models.Model.get_absolute_url for
            details.

            Must be implmented by child class.

            Raises:
                NotImplmentedError
        """
        raise NotImplmentedError
