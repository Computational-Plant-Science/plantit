'''
    The file manager handles interactions with a modular :mod:`filesystems`
    system to open connections with file servers that hold the files that
    make up a :class:`~plantit.collection.models.Sample`.

    Registering a file system
    ^^^^^^^^^^^^^^^^^^^^^^^^^
    Plant IT looks for file-system configurations in `django/filesystems.py`.
    All file systems subclass :class:`filesystems.AbstractStorageType`, which
    provides methods for connecting to the file system.

    There is currently support for local (:class:`filesystems.local.Local`) and
    and iRODS (:class:`filesystems.irods.IRods`) back ends.

    File systems are register with Plant IT using :attr:`filesystems.registrar`.
    The :attr:`filesystems.registrar` variable is an initialized
    :class:`filesystems.Registrar` object.

    Example:

        .. code-block:: python
            :caption: django/filesystems.py:

            from plantit.file_manager.filesystems.irods import IRods
            from plantit.file_manager.filesystems import registrar

            registrar.register(IRods(name = "irods",
                                     username = "rods",
                                     password = "rods",
                                     port = 1247,
                                     hostname = "irods",
                                     zone = "tempZone"),
                                lambda user: "/tempZone/home/rods/")

    See :class:`filesystems.Registrar` for registrar details.

    Opening a file
    ^^^^^^^^^^^^^^^
    :meth:`open` is provided as a convenience method for connecting to a file system.
    :meth:`open` respects file permissions.

    File Permissions
    ^^^^^^^^^^^^^^^^^
    A simple permission system is implemented in which only files down-tree of
    a user's default path are acceptable to a user.

    The user's default path is set at time of registering a file system.
    See :class:`filesystems.Registrar` and
    :mod:`~plantit.file_manager.permissions` for more details.
'''
from .filesystems import registrar

def open(storage_type, path):
    """
        Open a folder on a storage_type. Respecting permissions.

        Args:
            storage_type (str): name of a registered file storage system.
                strage_type must be a key in
                :attr:`plantit.file_manager.filesystems.registrar.list`
            path (str): path to open on the storage system.

        Returns:
            A file-like object open to the given path.
    """
    storage = registrar.list[storage_type]
    return storage.open(path)
