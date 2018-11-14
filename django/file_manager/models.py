from django.db import models
from .filesystems.storage import AbstractStorageType

class AbstractFile(models.Model):
    """
        Represents one file.

        Fields:
            storage (:class:`file_manager.filesystems.AbstractStorageType`):
                the type of storage the file is saved in. Must extend
                :class:`file_manager.filesystems.AbstractStorageType`
            path (str): the path to the file
            name (str): name of the file
    """
    path = models.CharField(max_length=250, unique=True)
    name = models.CharField(max_length=100)
    storage = models.ForeignKey(AbstractStorageType,on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name
