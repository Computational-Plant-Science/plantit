from django.db import models

from model_utils.managers import InheritanceManager

class AbstractStorageType(models.Model):
    """
        StorageTypes hold the information required to connect to a filesystem
        :class:`Storage` and an :meth:`open` method to open a connection
        to that filesystem. 
    """
    objects = InheritanceManager()
    name = models.CharField(max_length=25,unique=True)

    def open(self,path):
        """
            Open a connection to the storage system.

            Args:
                path (str): Path on the storage system to the folder to open
        """
        raise NotImplmentedError

    def __str__(self):
        return self.name
