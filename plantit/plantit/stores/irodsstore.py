import os
from pathlib import Path
from typing import List

from django.core.files.storage import Storage

from irods.session import iRODSSession
from irods.exception import CollectionDoesNotExist


# to be deprecated
class IRODSFileSystem(Storage):

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
        if name == "":
            return self.path
        elif self.path == "/":
            return "/" + name
        else:
            return self.path + "/" + name

    # def delete(self, name):
    #    path = self._mkpath(name)
    #    self.session.data_objects.

    def exists(self, name):
        path = self._mkpath(name)
        if self.session.data_objects.exists(path):
            return True
        else:
            try:
                self.session.collections.get(path)
                return True
            except CollectionDoesNotExist:
                return False

    def listdir(self, path):
        coll = self.session.collections.get(self._mkpath(path))
        files = [obj.name for obj in coll.data_objects]
        dirs = [obj.name for obj in coll.subcollections]
        return dirs, files

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


class IRODSOptions:
    def __init__(self, host: str, port: int, user: str, password: str, zone: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.zone = zone


class IRODS:
    def __init__(self, options: IRODSOptions):
        self.options = options

    def list(self, remote) -> List[str]:
        """
        Lists the files and directories at the given path on the remote IRODS instance.

        Args:
            remote: The remote path.

        Returns: The file/directory names.

        """
        remote = remote.rstrip("/")
        session = iRODSSession(host=self.options.host,
                               port=self.options.port,
                               user=self.options.user,
                               password=self.options.password,
                               zone=self.options.zone)

        if session.collections.exists(remote):
            collection = session.collections.get(remote)
            files = [file.name for file in collection.data_objects]
            directories = [directory.name for directory in collection.subcollections]
            return files + directories
        else:
            raise FileNotFoundError(f"Remote path '{remote}' does not exist")

    def get(self, remote, local):
        """
        Transfers the file or directory contents from the remote IRODS instance to the local file system.

        Args:
            remote: The remote file or directory path.
            local: The local directory path.
        """
        remote = remote.rstrip("/")
        Path(local).mkdir(parents=True, exist_ok=True)  # create local directory if it does not exist
        session = iRODSSession(host=self.options.host,
                               port=self.options.port,
                               user=self.options.user,
                               password=self.options.password,
                               zone=self.options.zone)

        if session.data_objects.exists(remote):
            session.data_objects.get(remote, file=os.path.join(local, os.path.basename(remote)))
        elif session.collections.exists(remote):
            collection = session.collections.get(remote)

            for file in collection.data_objects:
                self.get(os.path.join(remote, file.path), local)

            for sub_collection in collection.subcollections:
                nested = os.path.join(local, sub_collection.path.split("/")[-1])
                Path(nested).mkdir(exist_ok=True)
                self.get(os.path.join(remote, sub_collection.path), nested)
        else:
            raise FileNotFoundError(f"Remote path '{remote}' does not exist")

        session.cleanup()

    def put(self, local, remote):
        """
        Transfers the file or directory contents from the local file system to the remote IRODS instance.

        Args:
            local: The local file or directory path.
            remote: The remote directory path.
        """
        remote = remote.rstrip("/")
        session = iRODSSession(host=self.options.host,
                               port=self.options.port,
                               user=self.options.user,
                               password=self.options.password,
                               zone=self.options.zone)

        session.data_objects.put(local, remote)
        session.cleanup()

    def save(self, path, content):
        session = iRODSSession(host=self.options.host,
                               port=self.options.port,
                               user=self.options.user,
                               password=self.options.password,
                               zone=self.options.zone)
        file = session.data_objects.create(path)

        with file.open('r+') as f:
            f.write(content.read())

        return file.name

    def delete(self, path):
        session = iRODSSession(host=self.options.host,
                               port=self.options.port,
                               user=self.options.user,
                               password=self.options.password,
                               zone=self.options.zone)

        file = session.data_objects.get(path)
        session.data_objects.unlink(path)
        return file.name

    def read(self, path):
        session = iRODSSession(host=self.options.host,
                               port=self.options.port,
                               user=self.options.user,
                               password=self.options.password,
                               zone=self.options.zone)

        return session.data_objects.get(path).open('r')

    def create_collection(self, path):
        session = iRODSSession(host=self.options.host,
                               port=self.options.port,
                               user=self.options.user,
                               password=self.options.password,
                               zone=self.options.zone)

        session.collections.create(path)

    def delete_collection(self, path):
        session = iRODSSession(host=self.options.host,
                               port=self.options.port,
                               user=self.options.user,
                               password=self.options.password,
                               zone=self.options.zone)

        session.collections.remove(path, recurse=True, force=True)
