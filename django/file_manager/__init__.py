from .filesystems import registrar

def open(storage_type, path):
    """
        Open a folder on a storage_type

        Args:
            storage_type (str): name of a registered file system storage
            path (str): path to open
    """
    storage = registrar.list[storage_type]
    return storage.open(path)
