class AbstractStorageType:
    """
        StorageTypes hold the information required to connect to a filesystem
        :class:`Storage` and an :meth:`open` method to open a connection
        to that filesystem.
    """
    name = ""

    def open(self,path):
        """
            Open a connection to the storage system.

            Args:
                path (str): Path on the storage system to the folder to open
        """
        raise NotImplmentedError

    def __str__(self):
        return self.name
