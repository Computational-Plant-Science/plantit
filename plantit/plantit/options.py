import json
from typing import List
from abc import ABC


class BindMount:
    def __init__(self, host_path, container_path):
        self.host_path = host_path
        self.container_path = container_path


class Parameter:
    def __init__(self, key, value):
        self.key = key
        self.value = value


class FileChecksum:
    def __init__(self, file, checksum):
        self.file = file
        self.checksum = checksum


class Input(ABC):
    def __init__(self, path: str):
        self.__path = path

    @property
    def path(self):
        return self.__path


class FileInput(Input):
    def __init__(self, path: str):
        super().__init__(path)

    def to_json(self):
        return json.dumps(
            self,
            default=lambda o: dict((key, value) for key, value in o.__dict__.items() if value is not None),
            sort_keys=True,
            indent=4)


class DirectoryInput(Input):
    def __init__(self, path: str):
        super().__init__(path)

    def to_json(self):
        return json.dumps(
            self,
            default=lambda o: dict((key, value) for key, value in o.__dict__.items() if value is not None),
            sort_keys=True,
            indent=4)


class FilesInput(Input):
    def __init__(self, path: str, patterns: List[str] = None):
        super().__init__(path)
        self.patterns = patterns

    def to_json(self):
        return json.dumps(
            self,
            default=lambda o: dict((key, value) for key, value in o.__dict__.items() if value is not None),
            sort_keys=True,
            indent=4)


# noinspection PyShadowingBuiltins
class SubmissionOptions:
    def __init__(self,
                 workdir: str,
                 image: str,
                 command: str,
                 input: Input = None,
                 parameters: List[Parameter] = None,
                 bind_mounts: List[BindMount] = None,
                 checksums: List[FileChecksum] = None,
                 log_file: str = None,
                 jobqueue: dict = None,
                 no_cache: bool = False,
                 gpu: bool = False):
        self.workdir = workdir
        self.image = image
        self.command = command
        self.input = input
        self.parameters = parameters
        self.bind_mounts = bind_mounts
        self.checksums = checksums
        self.log_file = log_file
        self.jobqueue = jobqueue
        self.no_cache = no_cache
        self.gpu = gpu

    def to_json(self):
        return json.dumps(
            self,
            default=lambda o: dict((key, value) for key, value in o.__dict__.items() if value is not None),
            sort_keys=True,
            indent=4)


class CLIOptions(object):
    def __init__(self,
                 identifier: str,
                 workdir: str,
                 image: str,
                 command: str,
                 mount: list = None,
                 api_url: str = None,
                 clone: str = None,
                 branch: str = None,
                 plantit_token: str = None,
                 cyverse_token: str = None,
                 docker_username: str = None,
                 docker_password: str = None,
                 params: list = None,
                 input: dict = None,
                 output: dict = None,
                 logging: dict = None,
                 checksums: list = None,
                 slurm: dict = None):
        self.identifier = identifier
        self.workdir = workdir
        self.image = image
        self.mount = mount
        self.api_url = api_url
        self.command = command
        self.clone = clone
        self.branch = branch
        self.plantit_token = plantit_token
        self.cyverse_token = cyverse_token
        self.docker_username = docker_username
        self.docker_password = docker_password
        self.params = params
        self.input = input
        self.output = output
        self.logging = logging
        self.checksums = checksums
        self.slurm = slurm