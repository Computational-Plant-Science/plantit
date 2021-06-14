from typing import List, TypedDict

from enum import Enum


class BindMount(TypedDict):
    host_path: str
    container_path: str


class Parameter(TypedDict):
    key: str
    value: str


class Input(TypedDict, total=False):
    kind: str
    path: str
    patterns: List[str]


class InputKind(Enum):
    FILE = 1
    FILES = 2
    DIRECTORY = 3


class FileChecksum(TypedDict):
    file: str
    checksum: str


class PlantITCLIOptions(TypedDict, total=False):
    workdir: str
    image: str
    command: str
    input: Input
    output: dict
    parameters: List[Parameter]
    bind_mounts: List[BindMount]
    checksums: List[FileChecksum]
    log_file: str
    jobqueue: dict
    no_cache: bool
    gpu: bool
