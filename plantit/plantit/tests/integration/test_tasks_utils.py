from django.test import TestCase

from plantit.validation import validate_workflow_configuration
from plantit.tokens import TerrainToken


class TasksUtilsTests(TestCase):
    def test_validate_config_when_is_valid_with_input_file_and_empty_output(self):
        result = validate_workflow_configuration({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"',
            'input': {'path': '/iplant/home/shared/iplantcollaborative/testing_tools/cowsay/cowsay.txt', 'kind' : 'file'},
            'output': {'path': ''}
        })
        self.assertTrue(result)

    def test_validate_config_when_is_valid_with_input_file_and_nonempty_output(self):
        result = validate_workflow_configuration({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'image': 'docker://alpine',
            'commands': 'cat "$INPUT"',
            'input': {'path': '/iplant/home/shared/iplantcollaborative/testing_tools/cowsay/cowsay.txt',
                      'kind': 'file'},
            'output': {'path': 'outputdir'}
        })
        self.assertTrue(result)

    def test_validate_config_when_is_valid_with_input_files_and_empty_output(self):
        result = validate_workflow_configuration({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'image': 'docker://alpine',
            'commands': 'ls "$INPUT"',
            'input': {'path': '/iplant/home/shared/iplantcollaborative/testing_tools/cowsay',
                      'kind': 'files'},
            'output': {'path': ''}
        })
        self.assertTrue(result)

    def test_validate_config_when_is_valid_with_input_files_and_nonempty_output(self):
        result = validate_workflow_configuration({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'image': 'docker://alpine',
            'commands': 'ls "$INPUT" | tee output.txt',
            'input': {'path': '/iplant/home/shared/iplantcollaborative/testing_tools/cowsay',
                      'kind': 'files'},
            'output': {'path': 'outputdir'}
        })
        self.assertTrue(result)

    def test_validate_config_when_is_valid_with_input_directory_and_empty_output(self):
        result = validate_workflow_configuration({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'image': 'docker://alpine',
            'commands': 'ls "$INPUT"',
            'input': {'path': '/iplant/home/shared/iplantcollaborative/testing_tools/cowsay',
                      'kind': 'directory'},
            'output': {'path': ''}
        })
        self.assertTrue(result)

    def test_validate_config_when_is_valid_with_input_directory_and_nonempty_output(self):
        result = validate_workflow_configuration({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'image': 'docker://alpine',
            'commands': 'ls "$INPUT" | tee output.txt',
            'input': {'path': '/iplant/home/shared/iplantcollaborative/testing_tools/cowsay',
                      'kind': 'directory'},
            'output': {'path': 'outputdir'}
        })
        self.assertTrue(result)
