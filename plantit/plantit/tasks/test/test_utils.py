# from django.test import TestCase

# from plantit.ssh import execute_command, SSH


# class UtilsTests(TestCase):
#     def test_execute_command(self):
#         ssh = SSH('sandbox', 22, 'root', 'root')
#         with ssh:
#             lines = list(execute_command(ssh=ssh, precommand=':', command='pwd', directory='/root', allow_stderr=False))
#             self.assertEqual('/root\r\n', lines[0])
#
#     def test_execute_command_with_pre_command(self):
#         ssh = SSH('sandbox', 22, 'root', 'root')
#         with ssh:
#             lines = list(execute_command(ssh=ssh, precommand='pwd', command='pwd', directory='/root', allow_stderr=False))
#             self.assertEqual('/root\r\n', lines[0])
#             self.assertEqual('/root\r\n', lines[1])
