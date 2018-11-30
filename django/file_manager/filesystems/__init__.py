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
