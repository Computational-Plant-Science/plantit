import io

from django.test import TestCase

from irods.session import iRODSSession

from ..test.test_models import create_user

from plantit.file_manager.filesystems.irods import IRodsFileSystem


# Create your tests here.
class TestIRodsFileSystem(TestCase):
    """
        Attributes:
            filesystem (:class:`.filesystems.irods.IRodsFileSystem`): object
            session (:class:`irods.session.iRODSession`): opened with the same
                paramaters as the IRodsFileSystem object at self.filesystem
    """
    @classmethod
    def setUpTestData(cls):
        cls.host = "irods"
        cls.port = 1247
        cls.user = "rods"
        cls.password = "rods"
        cls.zone = "tempZone"

        cls.session = iRODSSession(host=cls.host,
                                port=cls.port,
                                user=cls.user,
                                password=cls.password,
                                zone=cls.zone)

        cls.filesystem = IRodsFileSystem(host = cls.host,
                                port = cls.port,
                                user = cls.user,
                                password = cls.password,
                                zone = cls.zone,
                                path = '/tempZone/')

    def test_listdir(self):
        dirs,files = self.filesystem.listdir("")

        self.assertEqual(dirs,['home','trash'])
        self.assertEqual(files,[])

    def test_exists(self):
        self.assertTrue(self.filesystem.exists('home'))
        self.assertFalse(self.filesystem.exists('SOME_NAME_THAT_WOULD_NEVER_EXIST'))

    def test_save(self):
        data = b'Some data to put inside a file'
        file = io.BytesIO(data)
        file_name = self.filesystem.save('file.test',file)

        saved_file = self.session.data_objects.get('/tempZone/' + file_name)
        with saved_file.open('r') as f:
            saved_data = f.read()
            self.assertEqual(saved_data,data)

        saved_file.unlink(force=True)

    def test_open(self):
        data = b'Some data to put inside a file'
        obj = self.session.data_objects.create('/tempZone/' + 'test.file')
        with obj.open('w') as f:
            f.write(data)

        file = self.filesystem.open('test.file')
        self.assertEqual(data,file.read())
        file.close()

        obj.unlink(force=True)
