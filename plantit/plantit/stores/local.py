from django.core.files.storage import FileSystemStorage
from .store import AbstractStorageType

class Local(AbstractStorageType):
    """
        Implements an AbstractStorageType for the FileSystemStorage storage type,
        which provides access to the web server's file system.
    """

    def __init__(self,name):
        self.name = name

    def open(self,path):
        return FileSystemStorage(path)
