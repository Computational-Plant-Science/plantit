from os.path import normpath
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.files.storage import FileSystemStorage

from .filesystems import registrar

"""
    File System Permissions.

    Used to check user access on a storage system.
"""

def open_folder(storage_type, path, user, *kwargs):
    """
        Open a connection to the file system containing the path, checking
        that the folder is equal to or child to the base_path provided
        by the storage system.

        Args:
            storage_type (str): name of the file system storage type must be
                subclass of AbstractStorageType
            path: Folder path
            user: User that has permission to the folder path
            *kwargs: unique paramaters for each STORAGE type
    """

    split_path = normpath(path).rstrip("/").split("/")
    split_base_path  = registrar.default_path(storage_type,user).rstrip("/").split("/")

    if split_base_path == split_path[0:len(split_base_path)]:
        storage = registrar.list[storage_type]
        return storage.open(path)

    raise PermissionDenied("Permission denied for path \"" + path +
                            "\" on storage \"" + storage_type +
                            "\" for user " + str(user))
