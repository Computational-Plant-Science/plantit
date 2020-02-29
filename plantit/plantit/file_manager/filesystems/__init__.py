class Registrar():
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

    def register(self,storage_type, default_path):
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

    def default_path(self,storage_type, user):
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
