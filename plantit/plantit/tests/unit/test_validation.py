from django.test import TestCase

from plantit.validation import validate_workflow_configuration


class ValidationTests(TestCase):
    def test_validate_config_when_is_not_valid_missing_name(self):
        valid, errors = validate_workflow_configuration({
            'author': 'Computational Plant Science Lab',
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"'
        })
        self.assertFalse(valid)
        self.assertTrue('Missing attribute \'name\'' in errors)

    def test_validate_config_when_is_not_valid_missing_image(self):
        result = validate_workflow_configuration({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'commands': 'echo "Hello, world!"'
        })
        self.assertFalse(result[0])
        self.assertTrue('Missing attribute \'image\'' in result[1])

    def test_validate_config_when_is_valid_image_with_comment(self):
        result = validate_workflow_configuration({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'commands': 'echo "Hello, world!"',
            'image': 'docker://alpine  # this is the image'
        })
        self.assertTrue(result[0])
        # self.assertTrue('Missing attribute \'image\'' in result[1])

    def test_validate_config_when_is_not_valid_shell_wrong_type(self):
        result = validate_workflow_configuration({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"',
            'shell': True
        })
        self.assertFalse(result[0])
        self.assertTrue('Attribute \'shell\' must be a str' in result[1])

    def test_validate_config_when_is_valid_shell_selections(self):
        result = validate_workflow_configuration({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"',
            'shell': 'bash'
        })
        self.assertTrue(result[0])

        result = validate_workflow_configuration({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"',
            'shell': 'sh'
        })
        self.assertTrue(result[0])

        result = validate_workflow_configuration({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"',
            'shell': 'zsh'
        })
        self.assertTrue(result[0])

    def test_validate_config_when_is_not_valid_unsupported_shell(self):
        result = validate_workflow_configuration({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"',
            'shell': 'not a supported shell'
        })
        self.assertFalse(result[0])
        self.assertTrue('Attribute \'shell\' must be \'sh\', \'bash\', or \'zsh\'' in result[1])

    def test_validate_config_when_is_not_valid_missing_commands(self):
        result = validate_workflow_configuration({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'image': 'docker://alpine',
        })
        self.assertFalse(result[0])
        self.assertTrue('Missing attribute \'commands\'' in result[1])

    def test_validate_config_when_is_not_valid_name_wrong_type(self):
        result = validate_workflow_configuration({
            'name': True,
            'author': 'Computational Plant Science Lab',
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"'
        })
        self.assertFalse(result[0])
        self.assertTrue('Attribute \'name\' must be a str' in result[1])

    # def test_validate_config_when_is_not_valid_author_wrong_type(self):
    #     result = validate_workflow_configuration({
    #         'name': 'Test Flow',
    #         'author': True,
    #         'image': 'docker://alpine',
    #         'commands': 'echo "Hello, world!"'
    #     }, Token.get())
    #     self.assertFalse(result[0])
    #     self.assertTrue('Attribute \'author\' must be a str' in result[1])

    def test_validate_config_when_is_not_valid_image_wrong_type(self):
        result = validate_workflow_configuration({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'image': True,
            'commands': 'echo "Hello, world!"'
        })
        self.assertFalse(result[0])
        self.assertTrue('Attribute \'image\' must be a str' in result[1])

    def test_validate_config_when_is_not_valid_commands_wrong_type(self):
        result = validate_workflow_configuration({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'image': 'docker://alpine',
            'commands': True
        })
        self.assertFalse(result[0])
        self.assertTrue('Attribute \'commands\' must be a str' in result[1])

    def test_validate_config_when_is_not_valid_mount_wrong_type(self):
        result = validate_workflow_configuration({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'image': True,
            'commands': 'echo "Hello, world!"',
            'mount': True,
        })
        self.assertFalse(result[0])
        self.assertTrue('Attribute \'mount\' must be a list' in result[1])

    def test_validate_config_when_is_not_valid_mount_none(self):
        result = validate_workflow_configuration({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'image': True,
            'commands': 'echo "Hello, world!"',
            'mount': None,
        })
        self.assertFalse(result[0])
        self.assertTrue('Attribute \'mount\' must be a list' in result[1])

    def test_validate_config_when_is_not_valid_mount_empty(self):
        result = validate_workflow_configuration({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'image': True,
            'commands': 'echo "Hello, world!"',
            'mount': [],
        })
        self.assertFalse(result[0])
        self.assertTrue('Attribute \'mount\' must not be empty' in result[1])

    def test_validate_config_when_is_valid_with_no_input_or_output(self):
        result = validate_workflow_configuration({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"'
        })
        self.assertTrue(result[0])

    def test_validate_config_when_is_valid_with_no_input_and_empty_output(self):
        result = validate_workflow_configuration({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"',
            'output': {}
        })
        self.assertTrue(result[0])

    def test_validate_config_when_is_valid_with_no_input_path_and_empty_output(self):
        result = validate_workflow_configuration({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'image': 'docker://alpine',
            'commands': 'cat $INPUT',
            'input': {
                'kind': 'file'
            },
            'output': {}
        })
        self.assertTrue(result[0])

    def test_validate_config_when_is_valid_with_no_input_and_empty_output_path(self):
        result = validate_workflow_configuration({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"',
            'output': {
                'path': '',
            }
        })
        self.assertTrue(result[0])

    def test_validate_config_when_is_valid_with_no_input_and_nonempty_output(self):
        result = validate_workflow_configuration({
            'name': 'Test Flow',
            'author': 'Computational Plant Science Lab',
            'image': 'docker://alpine',
            'commands': 'echo "Hello, world!"',
            'output': {
                'path': 'outputdir',
            }
        })
        self.assertTrue(result[0])
