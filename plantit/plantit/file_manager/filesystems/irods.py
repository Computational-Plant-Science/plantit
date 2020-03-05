from django.core.files.storage import Storage

from irods.session import iRODSSession
from irods.exception import CollectionDoesNotExist

from .storage import AbstractStorageType


class IRODSFileSystem(Storage):
    """
        Implements basic file stroage on a iRODS_ filesystem. It inherits from
        Storage and provides implementations for all the public methods thereof.

        .. _iRODS: https://irods.org/
    """

    def __init__(self, host, port, user, password, zone, path='/'):
        self.session = iRODSSession(host=host, port=port, user=user, password=password, zone=zone)

        self.path = "/" + path.strip('./')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.cleanup()

    def close(self):
        self.session.cleanup()

    def _mkpath(self, name):
        name = name.strip('./')
        if (name == ""):
            return self.path
        elif (self.path == "/"):
            return "/" + name
        else:
            return self.path + "/" + name

    def delete(self, name):
        raise NotImplementedError

    def exists(self, name):
        path = self._mkpath(name)
        if (self.session.data_objects.exists(path)):
            return True
        else:  # see if there is a collection by that name
            try:
                self.session.collections.get(path)
                return True
            except CollectionDoesNotExist:
                return False

    def listdir(self, path):
        coll = self.session.collections.get(self._mkpath(path))
        files = [obj.name for obj in coll.data_objects]
        dirs = [obj.name for obj in coll.subcollections]
        return (dirs, files)

    def _open(self, name, mode):
        obj = self.session.data_objects.get(self._mkpath(name))
        return obj.open(mode.replace("b", ""))

    def _save(self, name, content):
        obj = self.session.data_objects.create(self._mkpath(name))
        with obj.open('r+') as f:
            f.write(content.read())
        return obj.name

    def size(self, name):
        obj = self.session.data_objects.get(self._mkpath(name))
        return obj.size


class IRODS(AbstractStorageType):
    """
        Implementes an AbstractStorageType for the IRodsFileSystem storage type,
        which provides access to an iRODS_ server file system.

        Attributes:
            name: Server Name
            username: Login username
            password: Login password
            port: connection port
            hostname: hostname of server
            zone: irodsZone

        .. _iRODS: https://irods.org/
    """

    def __init__(self, name, username, password, hostname, zone, port=1247):
        self.name = name
        self.username = username
        self.password = password
        self.port = port
        self.hostname = hostname
        self.zone = zone

    def open(self, path):
        return IRODSFileSystem(host=self.hostname,
                               port=self.port,
                               user=self.username,
                               password=self.password,
                               zone=self.zone,
                               path=path)
