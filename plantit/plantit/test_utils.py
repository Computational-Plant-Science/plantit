import os
import requests
from django.test import TestCase
from plantit.utils import docker_image_exists, validate_flow_config, cyverse_path_exists


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

        print(f"Using CyVerse username '{cyverse_username}' and password '{cyverse_password}'")

        response = requests.get(
            'https://de.cyverse.org/terrain/token/cas',
            auth=(cyverse_username, cyverse_password)).json()
        Token.__token = response['access_token']

        return Token.__token


class UtilsTest(TestCase):
    def test_docker_container_exists_when_exists_is_true(self):
        self.assertTrue(docker_image_exists('alpine'))

    def test_docker_container_exists_when_doesnt_exist_is_false(self):
        self.assertFalse(docker_image_exists('notacontainer'))

    def test_cyverse_path_exists_when_doesnt_exist_is_false(self):
        result = cyverse_path_exists('/iplant/home/shared/iplantcollaborative/testing_tools/cowsay/cowsaid.txt', Token.get())
        self.assertFalse(result)

    def test_cyverse_path_exists_when_is_a_file_is_true(self):
        result = cyverse_path_exists('/iplant/home/shared/iplantcollaborative/testing_tools/cowsay/cowsay.txt', Token.get())
        self.assertTrue(result[0])
        self.assertEqual(result[1], 'file')

    def test_cyverse_path_exists_when_is_a_directory_is_true(self):
        result = cyverse_path_exists('/iplant/home/shared/iplantcollaborative/testing_tools/cowsay', Token.get())
        self.assertTrue(result[0])
        self.assertEqual(result[1], 'directory')

    def test_validate_config_when_is_not_valid_missing_name(self):
        result = validate_flow_config({
            'author': 'Computational Plant Science Lab',
            'public': True,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"'
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Missing attribute \'name\'' in result[1])

    def test_validate_config_when_is_not_valid_missing_author(self):
        result = validate_flow_config({
            'name': 'Test Flow',
            'public': True,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"'
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Missing attribute \'author\'' in result[1])

    def test_validate_config_when_is_not_valid_missing_public(self):
        result = validate_flow_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"'
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Missing attribute \'public\'' in result[1])

    def test_validate_config_when_is_not_valid_missing_image(self):
        result = validate_flow_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'commands': 'echo "Hello, world!"'
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Missing attribute \'image\'' in result[1])

    def test_validate_config_when_is_not_valid_missing_commands(self):
        result = validate_flow_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'image': 'docker://alpine',
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Missing attribute \'commands\'' in result[1])

    def test_validate_config_when_is_not_valid_name_wrong_type(self):
        result = validate_flow_config({
            'name': True,
            'author': 'Computational Plant Science Lab',
            'public': True,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"'
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Attribute \'name\' must be a str' in result[1])

    def test_validate_config_when_is_not_valid_author_wrong_type(self):
        result = validate_flow_config({
            'name': 'Test Flow',
            'author': True,
            'public': True,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"'
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Attribute \'author\' must be a str' in result[1])

    def test_validate_config_when_is_not_valid_public_wrong_type(self):
        result = validate_flow_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': '',
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"'
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Attribute \'public\' must be a bool' in result[1])

    def test_validate_config_when_is_not_valid_image_wrong_type(self):
        result = validate_flow_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'image': True,
            'commands': 'echo "Hello, world!"'
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Attribute \'image\' must be a str' in result[1])

    def test_validate_config_when_is_not_valid_commands_wrong_type(self):
        result = validate_flow_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'image': 'docker://alpine',
            'commands': True
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Attribute \'commands\' must be a str' in result[1])

    def test_validate_config_when_is_not_valid_mount_wrong_type(self):
        result = validate_flow_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'image': True,
            'commands': 'echo "Hello, world!"',
            'mount': True,
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Attribute \'mount\' must be a list' in result[1])

    def test_validate_config_when_is_not_valid_mount_none(self):
        result = validate_flow_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'image': True,
            'commands': 'echo "Hello, world!"',
            'mount': None,
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Attribute \'mount\' must be a list' in result[1])

    def test_validate_config_when_is_not_valid_mount_empty(self):
        result = validate_flow_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'image': True,
            'commands': 'echo "Hello, world!"',
            'mount': [],
        }, Token.get())
        self.assertFalse(result[0])
        self.assertTrue('Attribute \'mount\' must not be empty' in result[1])

    def test_validate_config_when_is_valid_with_no_input_or_output(self):
        result = validate_flow_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"'
        }, Token.get())
        self.assertTrue(result)

    def test_validate_config_when_is_valid_with_no_input_and_empty_file_output(self):
        result = validate_flow_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"',
            'output': {
                'path': '',
            }
        }, Token.get())
        self.assertTrue(result)

    def test_validate_config_when_is_valid_with_no_input_and_nonempty_output(self):
        result = validate_flow_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"',
            'output': {
                'path': 'outputdir',
            }
        }, Token.get())
        self.assertTrue(result)

    def test_validate_config_when_is_valid_with_input_file_and_empty_output(self):
        result = validate_flow_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"',
            'input': {'path': '/iplant/home/shared/iplantcollaborative/testing_tools/cowsay/cowsay.txt', 'kind' : 'file'},
            'output': {'path': ''}
        }, Token.get())
        self.assertTrue(result)

    def test_validate_config_when_is_valid_with_input_file_and_nonempty_output(self):
        result = validate_flow_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'image': 'docker://alpine',
            'commands': 'cat "$INPUT"',
            'input': {'path': '/iplant/home/shared/iplantcollaborative/testing_tools/cowsay/cowsay.txt',
                      'kind': 'file'},
            'output': {'path': 'outputdir'}
        }, Token.get())
        self.assertTrue(result)

    def test_validate_config_when_is_valid_with_input_files_and_empty_output(self):
        result = validate_flow_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'image': 'docker://alpine',
            'commands': 'ls "$INPUT"',
            'input': {'path': '/iplant/home/shared/iplantcollaborative/testing_tools/cowsay',
                      'kind': 'files'},
            'output': {'path': ''}
        }, Token.get())
        self.assertTrue(result)

    def test_validate_config_when_is_valid_with_input_files_and_nonempty_output(self):
        result = validate_flow_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'image': 'docker://alpine',
            'commands': 'ls "$INPUT" | tee output.txt',
            'input': {'path': '/iplant/home/shared/iplantcollaborative/testing_tools/cowsay',
                      'kind': 'files'},
            'output': {'path': 'outputdir'}
        }, Token.get())
        self.assertTrue(result)

    def test_validate_config_when_is_valid_with_input_directory_and_empty_output(self):
        result = validate_flow_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'image': 'docker://alpine',
            'commands': 'ls "$INPUT"',
            'input': {'path': '/iplant/home/shared/iplantcollaborative/testing_tools/cowsay',
                      'kind': 'directory'},
            'output': {'path': ''}
        }, Token.get())
        self.assertTrue(result)

    def test_validate_config_when_is_valid_with_input_directory_and_nonempty_output(self):
        result = validate_flow_config({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'public': True,
            'image': 'docker://alpine',
            'commands': 'ls "$INPUT" | tee output.txt',
            'input': {'path': '/iplant/home/shared/iplantcollaborative/testing_tools/cowsay',
                      'kind': 'directory'},
            'output': {'path': 'outputdir'}
        }, Token.get())
        self.assertTrue(result)
