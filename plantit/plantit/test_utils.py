import os
import requests
from django.test import TestCase
from plantit.utils import docker_container_exists, validate_config, cyverse_path_exists


class Token:
    __token = None

    @staticmethod
    def get():
        if Token.__token is not None:
            return Token.__token

        cyverse_username = os.environ.get('CYVERSE_USERNAME', None)
        cyverse_password = os.environ.get('CYVERSE_PASSWORD', None)

        if cyverse_username is None:
            raise ValueError("Missing environment variable 'CYVERSE_USERNAME'")
        if cyverse_password is None:
            raise ValueError("Missing environment variable 'CYVERSE_PASSWORD'")

        response = requests.get(
            'https://de.cyverse.org/terrain/token/cas',
            auth=(cyverse_username, cyverse_password)).json()
        Token.__token = response['access_token']

        return Token.__token


class UtilsTest(TestCase):
    def test_docker_container_exists_when_exists_is_true(self):
        self.assertTrue(docker_container_exists('alpine'))

    def test_docker_container_exists_when_doesnt_exist_is_false(self):
        self.assertFalse(docker_container_exists('notacontainer'))

    def test_cyverse_path_exists_when_doesnt_exist_is_false(self):
        self.assertFalse(cyverse_path_exists('/iplant/home/shared/iplantcollaborative/testing_tools/cowsay/cowsaid.txt', Token.get()))

    def test_cyverse_path_exists_when_is_a_file_is_true(self):
        self.assertTrue(cyverse_path_exists('/iplant/home/shared/iplantcollaborative/testing_tools/cowsay/cowsay.txt', Token.get()))

    def test_cyverse_path_exists_when_is_a_directory_is_true(self):
        self.assertTrue(cyverse_path_exists('/iplant/home/shared/iplantcollaborative/testing_tools/cowsay', Token.get()))

    def test_validate_config_when_is_not_valid_missing_name(self):
        result = validate_config({
            'author': 'Computational Plant Science Lab',
            'public': True,
            'clone': False,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"'
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Missing attribute \'name\'' in result[1])

    def test_validate_config_when_is_not_valid_missing_author(self):
        result = validate_config({
            'name': 'Test Flow',
            'public': True,
            'clone': False,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"'
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Missing attribute \'author\'' in result[1])

    def test_validate_config_when_is_not_valid_missing_public(self):
        result = validate_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'clone': False,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"'
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Missing attribute \'public\'' in result[1])

    def test_validate_config_when_is_not_valid_missing_clone(self):
        result = validate_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"'
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Missing attribute \'clone\'' in result[1])

    def test_validate_config_when_is_not_valid_missing_image(self):
        result = validate_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'clone': False,
            'commands': 'echo "Hello, world!"'
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Missing attribute \'image\'' in result[1])

    def test_validate_config_when_is_not_valid_missing_commands(self):
        result = validate_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'clone': False,
            'image': 'docker://alpine',
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Missing attribute \'commands\'' in result[1])

    def test_validate_config_when_is_not_valid_name_wrong_type(self):
        result = validate_config({
            'name': True,
            'author': 'Computational Plant Science Lab',
            'public': True,
            'clone': False,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"'
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Attribute \'name\' must be a str' in result[1])

    def test_validate_config_when_is_not_valid_author_wrong_type(self):
        result = validate_config({
            'name': 'Test Flow',
            'author': True,
            'public': True,
            'clone': False,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"'
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Attribute \'author\' must be a str' in result[1])

    def test_validate_config_when_is_not_valid_public_wrong_type(self):
        result = validate_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': '',
            'clone': False,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"'
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Attribute \'public\' must be a bool' in result[1])

    def test_validate_config_when_is_not_valid_clone_wrong_type(self):
        result = validate_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'clone': '',
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"'
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Attribute \'clone\' must be a bool' in result[1])

    def test_validate_config_when_is_not_valid_image_wrong_type(self):
        result = validate_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'clone': False,
            'image': True,
            'commands': 'echo "Hello, world!"'
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Attribute \'image\' must be a str' in result[1])

    def test_validate_config_when_is_not_valid_commands_wrong_type(self):
        result = validate_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'clone': False,
            'image': 'docker://alpine',
            'commands': True
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Attribute \'commands\' must be a str' in result[1])

    def test_validate_config_when_is_not_valid_with_no_input_but_from_directory(self):
        result = validate_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'clone': False,
            'commands': 'echo "Hello, world!"',
            'from_directory': True
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Attribute \'from_directory\' may only be configured in combination with attribute \'from\'' in result[1])

    def test_validate_config_when_is_valid_with_no_input_or_output(self):
        result = validate_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'clone': False,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"'
        }, Token.get())
        self.assertTrue(result)

    def test_validate_config_when_is_valid_with_no_input_and_empty_output(self):
        result = validate_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'clone': False,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"',
            'to': ''
        }, Token.get())
        self.assertTrue(result)

    def test_validate_config_when_is_valid_with_no_input_and_nonempty_output(self):
        result = validate_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'clone': False,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"',
            'to': 'outputdir'
        }, Token.get())
        self.assertTrue(result)

    def test_validate_config_when_is_valid_with_input_file_and_empty_output(self):
        result = validate_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'clone': False,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"',
            'from': '/iplant/home/shared/iplantcollaborative/testing_tools/cowsay/cowsay.txt',
            'to': ''
        }, Token.get())
        self.assertTrue(result)

    def test_validate_config_when_is_valid_with_input_file_and_nonempty_output(self):
        result = validate_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'clone': False,
            'image': 'docker://alpine',
            'commands': 'cat "$INPUT"',
            'from': '/iplant/home/shared/iplantcollaborative/testing_tools/cowsay/cowsay.txt',
            'to': 'outputdir'
        }, Token.get())
        self.assertTrue(result)

    def test_validate_config_when_is_valid_with_input_files_and_empty_output(self):
        result = validate_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'clone': False,
            'image': 'docker://alpine',
            'commands': 'ls "$INPUT"',
            'from': '/iplant/home/shared/iplantcollaborative/testing_tools/cowsay',
            'to': ''
        }, Token.get())
        self.assertTrue(result)

    def test_validate_config_when_is_valid_with_input_files_and_nonempty_output(self):
        result = validate_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'clone': False,
            'image': 'docker://alpine',
            'commands': 'ls "$INPUT" | tee output.txt',
            'from': '/iplant/home/shared/iplantcollaborative/testing_tools/cowsay',
            'to': 'outputdir'
        }, Token.get())
        self.assertTrue(result)

    def test_validate_config_when_is_valid_with_input_directory_and_empty_output(self):
        result = validate_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'clone': False,
            'image': 'docker://alpine',
            'commands': 'ls "$INPUT"',
            'from': '/iplant/home/shared/iplantcollaborative/testing_tools/cowsay',
            'from_directory': True,
            'to': ''
        }, Token.get())
        self.assertTrue(result)

    def test_validate_config_when_is_valid_with_input_directory_and_nonempty_output(self):
        result = validate_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'clone': False,
            'image': 'docker://alpine',
            'commands': 'ls "$INPUT" | tee output.txt',
            'from': '/iplant/home/shared/iplantcollaborative/testing_tools/cowsay',
            'from_directory': True,
            'to': 'outputdir'
        }, Token.get())
        self.assertTrue(result)
