from os import environ
from django.test import TestCase

import plantit.mapbox as mapbox


class MapboxTest(TestCase):
    async def test_get_institution(self):
        result = await mapbox.get_institution("University of Georgia", environ.get('MAPBOX_TOKEN'))
        self.assertTrue('university' in result['query'] and 'of' in result['query'] and 'georgia' in result['query'])
        self.assertTrue(len(result['features']) > 0)
