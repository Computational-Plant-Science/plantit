import yaml
from django.test import TestCase
from plantit.utils import docker_container_exists, validate_config


class UtilsTest(TestCase):
    def test_docker_container_exists_when_exists_is_true(self):
        self.assertTrue(docker_container_exists('alpine'))

    def test_docker_container_exists_when_doesnt_exist_is_false(self):
        self.assertFalse(docker_container_exists('notacontainer'))

    def test_validate_config_when_is_not_valid_missing_name(self):
        self.assertFalse(validate_config({
            'author': 'Computational Plant Science Lab',
            'public': True,
            'clone': False,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"'
        })[0])

    def test_validate_config_when_is_not_valid_missing_author(self):
        self.assertFalse(validate_config({
            'name': 'Test Flow',
            'public': True,
            'clone': False,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"'
        })[0])

    def test_validate_config_when_is_not_valid_missing_public(self):
        self.assertFalse(validate_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'clone': False,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"'
        })[0])

    def test_validate_config_when_is_not_valid_missing_clone(self):
        self.assertFalse(validate_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"'
        })[0])

    def test_validate_config_when_is_not_valid_missing_image(self):
        self.assertFalse(validate_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'clone': False,
            'commands': 'echo "Hello, world!"'
        })[0])

    def test_validate_config_when_is_not_valid_missing_commands(self):
        self.assertFalse(validate_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'clone': False,
            'image': 'docker://alpine',
        })[0])

    def test_validate_config_when_is_valid_with_no_input_or_output(self):
        self.assertTrue({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'clone': False,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"'
        })

    def test_validate_config_when_is_valid_with_no_input_and_empty_output(self):
        self.assertTrue({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'clone': False,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"',
            'to': ''
        })

    def test_validate_config_when_is_valid_with_no_input_and_nonempty_output(self):
        self.assertTrue({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'clone': False,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"',
            'to': 'outputdir'
        })

    def test_validate_config_when_is_valid_with_input_file_and_empty_output(self):
        self.assertTrue({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'clone': False,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"',
            'from': '/iplant/home/shared/iplantcollaborative/testing_tools/cowsay/cowsay.txt',
            'to': ''
        })

    def test_validate_config_when_is_valid_with_input_file_and_nonempty_output(self):
        self.assertTrue({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'clone': False,
            'image': 'docker://alpine',
            'commands': 'cat "$INPUT"',
            'from': '/iplant/home/shared/iplantcollaborative/testing_tools/cowsay/cowsay.txt',
            'to': 'outputdir'
        })
