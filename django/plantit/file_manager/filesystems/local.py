from django.core.files.storage import FileSystemStorage
from .storage import AbstractStorageType

class Local(AbstractStorageType):
    """
        Implementes an AbstractStorageType for the FileSystemStorage storage type,
            which provides access to the webserver's filesystem.
    """

    def __init__(self,name):
        self.name = name

    def open(self,path):
        return FileSystemStorage(path)
