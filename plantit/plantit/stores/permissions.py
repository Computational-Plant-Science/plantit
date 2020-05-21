from os.path import normpath
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.files.storage import FileSystemStorage

from plantit.stores import registrar

"""
    File System Permissions.

    Used to check user access on a storage system.
"""

def open_folder(storage_type, path, user):
    """
        Open a connection to the file system containing the path, checking
        that the folder is equal to or child to the base_path provided
        by the storage system.

        Args:
            storage_type (str): name of the file system storage type must be
             a key in :attr:`plantit.file_manager.filesystems.Registrar.list`
            path (str): folder path
            user (:class:`~django.contrib.auth.models.User`):
                user that has permission to the folder path

        Returns:
            A file-like object open to the given path.
    """

    split_path = normpath(path).rstrip("/").split("/")
    split_base_path  = registrar.default_path(storage_type,user).rstrip("/").split("/")

    if split_base_path == split_path[0:len(split_base_path)]:
        storage = registrar.list[storage_type]
        return storage.open(path)

    raise PermissionDenied("Permission denied for path \"" + path +
                            "\" on storage \"" + storage_type +
                            "\" for user " + str(user))
