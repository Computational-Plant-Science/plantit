from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.files.storage import FileSystemStorage

from .filesystems import registrar

"""
    Folder-level persmission system. Default permissions for a user are
    no access.
"""

class Location(models.Model):
    ##TODO: delete a folder entry if no Permissions objects link to it
    path = models.TextField()
    storage_type = models.CharField(max_length=50)

    def __str__(self):
        return "%s on %s"%(self.path,self.storage_type)

class Permissions(models.Model):
    """
        Per-user folder-level permissions. Default permissions are no access.

        Attributes:
            user (:class:`User`): ForeignKey of user with permissions
            folders (:class:`Folder`): ManytoMany of the locations with access permission
    """
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    location = models.ManyToManyField(Location)

    def __str__(self):
        return str(self.user)

    @staticmethod
    def normalize_path(path):
        return path.strip("/.")

    @staticmethod
    def allow(user,storage_type,folder):
        """
            Permit a user to access a folder.

            Args:
                user (:class:`User`): The user to permit
                storage_type (:class:AbstractStorageType): The storage backend
                    where the folder is contained
                folder (str): folder path
        """
        perms, _ = Permissions.objects.get_or_create(user=user)
        folder, _ = Location.objects.get_or_create(storage_type=storage_type,path=Permissions.normalize_path(folder))

        perms.location.add(folder)

    @staticmethod
    def revoke(user,storage_type,folder):
        """
            Revoke folder access from a user.

            Args:
                user (:class:`User`): The user to permit
                storage_type  (:class:AbstractStorageType): The storage backend
                    where the folder is contained
                folder (str): folder path
        """
        perms, _ = Permissions.objects.get_or_create(user=user)
        queryset = perms.location.filter(storage_type=storage_type,
                                    path__startswith=Permissions.normalize_path(folder))
        perms.location.remove(*queryset)

    @staticmethod
    def allowed(user,storage_type,path):
        """
            Check if the user for this permissions object has access to a given
            folder.

            .. warning::
                References to parent folders using '../' are always denined.
                See :meth:`tests.test_parent_folder_access` for why.

            .. todo::
                Better handle references to parent ('../') directories

            Args:
                storage_type (str): The storage backend where the folder is contained
                path (str): folder path
            Retruns:
                bool: True if user has permission to access folder, False otheriwse
        """
        try:
            perms = Permissions.objects.get(user=user)
        except Permissions.DoesNotExist:
            return False
        if(".." in path):
            return False
        if(perms.location.filter(storage_type=storage_type,path="/").exists()):
            return True #<- all locations allowed
        folders = Permissions.normalize_path(path).split("/")
        path_list = ["/".join(folders[0:(i+1)]) for i in range(len(folders))]
        return perms.location.filter(storage_type=storage_type,path__in=path_list).exists()

def open_folder(storage_type, path, user, *kwargs):
    """
        Open a connection to the file system containing the path, observing
        permissions.

        Args:
            storage_type (str): name of the file system storage type must be
                subclass of AbstractStorageType
            path: Folder path
            user: User that has permission to the folder path
            *kwargs: unique paramaters for each STORAGE type
    """
    if not Permissions.allowed(user = user,
                            storage_type = storage_type,
                            path = path):
        raise PermissionDenied

    storage = registrar.list[storage_type]

    return storage.open(path)
