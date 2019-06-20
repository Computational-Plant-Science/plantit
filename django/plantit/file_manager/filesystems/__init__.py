class Registrar():
    """
        Keeps a list of registered filesystems
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
                storage_type (:class:`file_manager.filesystems.storage.AbstractStorageType`):
                    the storage object
                default_location (function): A function that returns the default
                    base storage path. The function is passed the username
                    of the requesting user
        """

        assert default_path("test_user")[-1] == "/", "Default paths must end with a \"/\""
        assert default_path("test_user")[0] == "/", "Default path must be absoltue (start with a \"/\")"

        self.list[storage_type.name] = storage_type
        self.default_basename[storage_type.name] = default_path

    def default_path(self,storage_type, user):
        return self.default_basename[storage_type](user)

registrar = Registrar()

try:
    from filesystems import *
except ImportError as e:
    print(e)
    pass
