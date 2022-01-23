from pprint import pprint

from django.test import TestCase

import plantit.queries as q


class QueriesTests(TestCase):
    async def test_get_institutions(self):
        institutions = await q.get_institutions()
        pprint(institutions)
