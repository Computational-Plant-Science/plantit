from django.test import TestCase
from tenacity import RetryError
from requests import HTTPError

from plantit.terrain import refresh_tokens, get_dirs_async
from plantit.tokens import TerrainToken


class TerrainTest(TestCase):
    def test_refresh_tokens_throws_error_when_access_token_is_invalid(self):
        with self.assertRaises(HTTPError) as e:
            pass
            # refresh_tokens('wbonelli', 'not a token')
            # self.assertTrue('401' in str(e))
