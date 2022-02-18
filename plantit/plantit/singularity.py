from typing import List
import logging

from plantit.tasks.models import Task, InputKind, TaskOptions, Parameter, EnvironmentVariable, BindMount
from plantit.utils.tasks import format_bind_mount

logger = logging.getLogger(__name__)


def compose_singularity_invocation(
        work_dir: str,
        image: str,
        commands: str,
        env: List[EnvironmentVariable] = None,
        bind_mounts: List[BindMount] = None,
        parameters: List[Parameter] = None,
        no_cache: bool = False,
        gpus: int = 0,
        shell: str = None,
        docker_username: str = None,
        docker_password: str = None,
        index: int = None) -> List[str]:
    command = ''

    # prepend environment variables in SINGULARITYENV_<key> format
    if env is not None:
        if len(env) > 0: command += ' '.join([f"SINGULARITYENV_{v['key'].upper().replace(' ', '_')}=\"{v['value']}\"" for v in env])
        command += ' '

    # substitute parameters
    if parameters is None: parameters = []
    if index is not None: parameters.append(Parameter(key='INDEX', value=str(index)))
    parameters.append(Parameter(key='WORKDIR', value=work_dir))
    for parameter in parameters:
        key = parameter['key'].upper().replace(' ', '_')
        val = str(parameter['value'])
        command += f" SINGULARITYENV_{key}=\"{val}\""

    # singularity invocation and working directory
    command += f" singularity exec --home {work_dir}"

    # add bind mount arguments
    if bind_mounts is not None and len(bind_mounts) > 0:
        command += (' --bind ' + ','.join([format_bind_mount(work_dir, mount_point) for mount_point in bind_mounts]))

    # whether to use the Singularity cache
    if no_cache: command += ' --disable-cache'

    # whether to use GPUs (Nvidia)
    if gpus: command += ' --nv'

    # append the command
    if shell is None: shell = 'sh'
    command += f" {image} {shell} -c '{commands}'"

    # don't want to reveal secrets, so log the command before prepending secret env vars
    logger.debug(f"Using command: '{command}'")

    # docker auth info (optional)
    if docker_username is not None and docker_password is not None:
        command = f"SINGULARITY_DOCKER_USERNAME={docker_username} SINGULARITY_DOCKER_PASSWORD={docker_password} " + command

    return [command]
