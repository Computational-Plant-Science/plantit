from .local import Local
from .irods import IRods
from plantit import secret

class Registrar():
    """
        Keeps a list of registered filesystems
    """
    list = {}

    def register(self,storage_type):
        """
            Register a storage type

            Args:
                storage_type (:class:`file_manager.filesystems.storage.AbstractStorageType`):
                    the storage object
        """
        self.list[storage_type.name] = storage_type

registrar = Registrar()



registrar.register(IRods(name = "irods",
                         username = secret.IRODS_USERNAME,
                         password = secret.IRODS_PASSWORD,
                         hostname = secret.IRODS_HOSTNAME,
                         zone = secret.IRODS_ZONE))

registrar.register(Local("local"))
