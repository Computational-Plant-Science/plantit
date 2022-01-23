from django.test import TestCase

from plantit.docker import image_exists


class DockerTest(TestCase):
    def test_docker_container_exists_when_exists_is_true(self):
        self.assertTrue(image_exists('alpine'))

    def test_docker_container_exists_when_doesnt_exist_is_false(self):
        self.assertFalse(image_exists('notacontainer'))
