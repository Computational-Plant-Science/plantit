from django.db import models

from job_manager.contrib import File as JobFile
from file_manager.models import AbstractFile
from workflows.models import AbstractDefaults, Tag, AbstractMetaData, AbstractCollection

"""
    Workflow for the DIRT2D code.
"""

class Defaults(AbstractDefaults):
    """
        Default Collection/Job Values

        Contains the default submission_script, files, and paramaters required
        to create a :class:`job_manager.contrib.SubmissionTask`.

        Attributes:
            submission_script (ForeignKey): the :class:`job_manager.contrib.File`
                that is run by the cluster as {sub_script}
                (see :class:`job_manager.models.Cluster`) upon submissionself.
            files (ManyToMany): Supporting :class:`job_manager.contrib.File`
                that are also copied to the cluster on submission
            parameters (TextField): parameters passed to the submission_script
    """
    submission_script = models.ForeignKey(JobFile,
                                        blank=True,
                                        null=True,
                                        on_delete=models.SET_NULL,
                                        related_name="submission_script")
    files = models.ManyToManyField(JobFile,blank=True)
    parameters = models.TextField(null=True,blank=True)

class MetaData(AbstractMetaData):
    """
        Metadata

        Attributes:
            key (str): Metadata key
            value (str): Metadata value
    """
    pass

class RootImage(AbstractFile):
    """
        Represents one root image file.

        Attributes:
            path (str): the path to the file
            name (str): name of the file
            metadata (ManyToManyField): User configurable metadata
    """
    metadata = models.ManyToManyField(MetaData,blank=True)

class RootCollection(AbstractCollection):
    """
        Contains a collection of root images that are analyzed togeather.
        Typically representing one experiment or treatment

        Attributes:
            name (str): the name of the collection
            description (str): text description
            user (ForeignKey): primary user for the collection
            images (ManyToMany): root images (:class:`.models.RootImage`) within
                the collection
            metadata (ForeignKey): User configurable metadata
                (:class:`.models.MetaData`)
    """
    images = models.ManyToManyField(RootImage,blank=True)
    metadata = models.ManyToManyField(MetaData,blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return "/workflows/dirt2d/collection/%d/details"%(self.pk,)
