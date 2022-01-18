from django.test import TestCase

from plantit.terrain import path_exists
from plantit.tokens import TerrainToken


class TerrainTest(TestCase):
    def test_cyverse_path_exists_when_doesnt_exist_is_false(self):
        result = path_exists('/iplant/home/shared/iplantcollaborative/testing_tools/cowsay/cowsaid.txt', TerrainToken.get())
        self.assertFalse(result)

    def test_cyverse_path_exists_when_is_a_file_is_true(self):
        result = path_exists('/iplant/home/shared/iplantcollaborative/testing_tools/cowsay/cowsay.txt', TerrainToken.get())
        self.assertTrue(result[0])
        self.assertEqual(result[1], 'file')

    def test_cyverse_path_exists_when_is_a_directory_is_true(self):
        result = path_exists('/iplant/home/shared/iplantcollaborative/testing_tools/cowsay', TerrainToken.get())
        self.assertTrue(result[0])
        self.assertEqual(result[1], 'directory')