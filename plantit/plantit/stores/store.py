class AbstractStorageType:
    """
        StorageTypes hold the information required to connect to a file system
        and an :meth:`open` method to open a connection to that file system.
    """
    name = ""

    def open(self,path):
        """
            Open a connection to the storage system.

            Args:
                path (str): Path on the storage system to the folder to open

            Returns:
                A file-like object open to the given path.
        """
        raise NotImplementedError

    def __str__(self):
        return self.name
