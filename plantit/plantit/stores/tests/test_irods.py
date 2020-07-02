import os
import tempfile

from django.test import TestCase

from irods.session import iRODSSession

from plantit.stores.irodsstore import IRODSFileSystem, IRODS, IRODSOptions


class TestIRODS(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.host = "irods"
        cls.port = 1247
        cls.user = "rods"
        cls.password = "rods"
        cls.zone = "tempZone"
        cls.data = "Hello, world!"
        cls.local_dir = tempfile.gettempdir()
        cls.remote_dir = f"/{cls.zone}"
        cls.session = iRODSSession(host=cls.host,
                                   port=cls.port,
                                   user=cls.user,
                                   password=cls.password,
                                   zone=cls.zone)
        cls.filesystem = IRODSFileSystem(host=cls.host,
                                         port=cls.port,
                                         user=cls.user,
                                         password=cls.password,
                                         zone=cls.zone,
                                         path=cls.remote_dir)
        cls.irods = IRODS(IRODSOptions(host="irods", port=1247, user="rods", zone=cls.zone, password="rods"))

    def test_list(self):
        local_file = tempfile.NamedTemporaryFile()
        local_path = local_file.name
        remote_file_path = os.path.join(self.remote_dir, local_file.name.split('/')[-1])
        remote_coll_path = os.path.join(self.remote_dir, "testCollection")

        try:
            self.session.collections.create(remote_coll_path)
            self.session.data_objects.put(local_path, remote_file_path)
            local_file.close()

            listed = self.irods.list(self.remote_dir)
            print(listed)

            self.assertTrue(remote_file_path.split('/')[-1] in listed)
            self.assertTrue(remote_coll_path.split('/')[-1] in listed)
        finally:
            self.session.data_objects.unlink(remote_file_path, force=True)
            self.session.collections.remove(remote_coll_path, force=True)

    def test_irods_get(self):
        local_file = tempfile.NamedTemporaryFile()
        local_path = local_file.name
        remote_path = os.path.join(self.remote_dir, local_file.name.split('/')[-1])

        try:
            with open(local_path, 'w') as file:
                file.write(self.data)

            self.session.data_objects.put(local_path, remote_path)
            local_file.close()

            self.irods.get(remote_path, self.local_dir)
            self.assertTrue(os.path.isfile(local_path))

            with open(local_path) as file:
                lines = file.readlines()
                self.assertEqual(len(lines), 1)
                self.assertEqual(lines[0], self.data)
        finally:
            self.session.data_objects.unlink(remote_path, force=True)

    def test_irods_put(self):
        local_file = tempfile.NamedTemporaryFile()
        local_path = local_file.name
        remote_path = os.path.join(self.remote_dir, local_file.name.split('/')[-1])

        try:
            with open(local_path, 'w') as file:
                file.write(self.data)

            self.irods.put(local_path, remote_path)
            local_file.close()

            self.session.data_objects.get(remote_path, self.local_dir)
            self.assertTrue(os.path.isfile(local_path))

            with open(local_path) as file:
                lines = file.readlines()
                self.assertEqual(len(lines), 1)
                self.assertEqual(lines[0], self.data)
        finally:
            self.session.data_objects.unlink(remote_path, force=True)

