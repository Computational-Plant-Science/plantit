from django.test import TestCase
from tenacity import RetryError
from requests import HTTPError

from plantit.terrain import path_exists
from plantit.tokens import TerrainToken


class TerrainTest(TestCase):
    def test_cyverse_path_exists_when_doesnt_exist_is_false(self):
        exists = path_exists('/iplant/home/shared/iplantcollaborative/testing_tools/cowsay/cowsaid.txt', TerrainToken.get())
        self.assertFalse(exists)

    def test_cyverse_path_exists_when_is_a_file_is_true(self):
        exists = path_exists('/iplant/home/shared/iplantcollaborative/testing_tools/cowsay/cowsay.txt', TerrainToken.get())
        self.assertTrue(exists)

    def test_cyverse_path_exists_when_is_a_directory_is_true(self):
        exists = path_exists('/iplant/home/shared/iplantcollaborative/testing_tools/cowsay', TerrainToken.get())
        self.assertTrue(exists)

    def test_throws_error_when_terrain_token_is_invalid(self):
        with self.assertRaises(HTTPError) as e:
            path_exists('/iplant/home/shared/iplantcollaborative/testing_tools/cowsay', 'not a token')
            self.assertTrue('401' in str(e))
