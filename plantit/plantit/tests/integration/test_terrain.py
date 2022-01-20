from django.test import TestCase

from plantit.terrain import path_exists
from plantit.tokens import TerrainToken


class TerrainTest(TestCase):
    def test_cyverse_path_exists_when_doesnt_exist_is_false(self):
        exists, type = path_exists('/iplant/home/shared/iplantcollaborative/testing_tools/cowsay/cowsaid.txt', TerrainToken.get())
        self.assertFalse(exists)
        self.assertIsNone(type)

    def test_cyverse_path_exists_when_is_a_file_is_true(self):
        exists, type = path_exists('/iplant/home/shared/iplantcollaborative/testing_tools/cowsay/cowsay.txt', TerrainToken.get())
        self.assertTrue(exists)
        self.assertEqual(type, 'file')

    def test_cyverse_path_exists_when_is_a_directory_is_true(self):
        exists, type = path_exists('/iplant/home/shared/iplantcollaborative/testing_tools/cowsay', TerrainToken.get())
        self.assertTrue(exists)
        self.assertEqual(type, 'directory')