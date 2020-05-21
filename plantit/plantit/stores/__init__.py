'''
    The file manager handles interactions with a modular :mod:`filesystems`
    system to open connections with file servers that hold the files that
    make up a :class:`~plantit.collection.models.Sample`.

    Registering a file system
    ^^^^^^^^^^^^^^^^^^^^^^^^^
    Plant IT looks for file-system configurations in `plantit/filesystems.py`.
    All file systems subclass :class:`filesystems.AbstractStorageType`, which
    provides methods for connecting to the file system.

    There is currently support for local (:class:`filesystems.local.Local`) and
    and iRODS (:class:`filesystems.irods.IRods`) back ends.

    File systems are register with Plant IT using :attr:`filesystems.registrar`.
    The :attr:`filesystems.registrar` variable is an initialized
    :class:`filesystems.Registrar` object.

    Example:

        .. code-block:: python
            :caption: plantit/filesystems.py:

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
class Registrar:
    """
        A registry of file systems registered with Plant IT.

        Note:
            This class should not used directly. A instance of this class at
            :attr:`plantit.file_manager.filesystems.registrar` should be used
            for registration of file systems. See :mod:`file_manager` for
            an example.

        Attributes:
            list (dict): key: storage object name. value: the sorage object
            default_basename (dict): key: storage object name.
                value: a function `func(user)` that returns the default
                base file path given a django user object.

    """

    def __init__(self):
        self.list = {}
        self.default_basename = {}

    def register(self, storage_type, default_path):
        """
            Register a storage type

            Attention:
                The path string returned by default_path must be absolute
                (start with a "/"), and end with a "/".

                The presence of these /s is checked by register, the web server
                will fail to start if the /s are missing.

            Args:
                storage_type (str): name of a registered file storage system.
                    storage_type must be a key in
                    :attr:`plantit.file_manager.filesystems.registrar.list`
                default_location (function): A function that returns the default
                    base storage path. The function is passed the user object
                    of the requesting user
        """

        assert default_path("test_user")[-1] == "/", "Default paths must end with a \"/\""
        assert default_path("test_user")[0] == "/", "Default path must be absoltue (start with a \"/\")"

        self.list[storage_type.name] = storage_type
        self.default_basename[storage_type.name] = default_path

    def default_path(self, storage_type, user):
        """
            Get the default path for a user on a storage type.

            Args:
                storage_type (str): name of a registered file storage system.
                    storage_type must be a key in
                    :attr:`plantit.file_manager.filesystems.registrar.list`
                user (django user): the user to calculate the base file path
                    for.
        """
        return self.default_basename[storage_type](user)


registrar = Registrar()


try:
    from filesystems import *
except ImportError as e:
    print(e)
    pass

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
