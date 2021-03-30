from os.path import isdir
from random import choice
from typing import List

import requests
import yaml
from requests.auth import HTTPBasicAuth

from plantit import settings
from plantit.options import BindMount, Parameter, RunOptions, DirectoryInput, FilesInput, FileInput


def get_repo_config(name, owner, token):
    print(f"Getting config for {owner}/{name}")
    request = requests.get(
        f"https://api.github.com/repos/{owner}/{name}/contents/plantit.yaml") if token == '' \
        else requests.get(f"https://api.github.com/repos/{owner}/{name}/contents/plantit.yaml",
                          headers={"Authorization": f"token {token}"})
    file = request.json()
    content = requests.get(file['download_url']).text
    config = yaml.load(content)

    # fill optional attributes
    config['public'] = config['public'] if 'public' in config else True

    return config


def get_repo_config_internal(name, owner):
    request = requests.get(
        f"https://api.github.com/repos/{owner}/{name}/contents/plantit.yaml", auth=HTTPBasicAuth(settings.GITHUB_USERNAME, settings.GITHUB_KEY))
    file = request.json()
    content = requests.get(file['download_url']).text
    return yaml.load(content)


def docker_image_exists(name, owner=None, tag=None):
    url = f"https://hub.docker.com/v2/repositories/{owner if owner is not None else 'library'}/{name}/"
    if tag is not None:
        url += f"tags/{tag}/"
    response = requests.get(url)
    try:
        content = response.json()
        if 'user' not in content and 'name' not in content:
            return False
        if content['name'] != tag and content['name'] != name and content['user'] != (owner if owner is not None else 'library'):
            return False
        return True
    except:
        return False


def cyverse_path_exists(path, token):
    response = requests.get(f"https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path={path}", headers={"Authorization": f"Bearer {token}"})
    content = response.json()
    input_type = 'directory'
    if response.status_code != 200:
        if 'error_code' not in content or ('error_code' in content and content['error_code'] == 'ERR_DOES_NOT_EXIST'):
            path_split = path.rpartition('/')
            base = path_split[0]
            file = path_split[2]
            up_response = requests.get(f"https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path={base}",
                         headers={"Authorization": f"Bearer {token}"})
            up_content = up_response.json()
            if up_response.status_code != 200:
                if 'error_code' not in up_content:
                    print(f"Unknown error: {up_content}")
                    return False
                elif 'error_code' in up_content:
                    print(f"Error: {up_content['error_code']}")
                    return False
            elif 'files' not in up_content:
                print(f"Directory '{base}' does not exist")
                return False
            elif len(up_content['files']) != 1:
                print(f"Multiple files found in directory '{base}' matching name '{file}'")
                return False
            elif up_content['files'][0]['label'] != file:
                print(f"File '{file}' does not exist in directory '{base}'")
                return False
            else:
                input_type = 'file'
        else:
            return False
    return True, input_type


def parse_docker_image_components(value):
    container_split = value.split('/')
    container_name = container_split[-1]
    container_owner = None if container_split[-2] == '' else container_split[-2]
    if ':' in container_name:
        container_name_split = container_name.split(":")
        container_name = container_name_split[0]
        container_tag = container_name_split[1]
    else:
        container_tag = None

    return container_owner, container_name, container_tag


def validate_workflow_config(config, token):
    errors = []

    # name (required)
    if 'name' not in config:
        errors.append('Missing attribute \'name\'')
    elif type(config['name']) is not str:
        errors.append('Attribute \'name\' must be a str')

    # author (optional)
    if 'author' in config and type(config['author']) is not str:
        errors.append('Attribute \'author\' must be a str')

    # public (required)
    if 'public' not in config:
        errors.append('Missing attribute \'public\'')
    elif type(config['public']) is not bool:
        errors.append('Attribute \'public\' must be a bool')

    # image (required)
    if 'image' not in config:
        errors.append('Missing attribute \'image\'')
    elif type(config['image']) is not str:
        errors.append('Attribute \'image\' must be a str')
    else:
        image_owner, image_name, image_tag = parse_docker_image_components(config['image'])
        if 'docker' in config['image'] and not docker_image_exists(image_name, image_owner, image_tag):
            errors.append(f"Image '{config['image']}' not found on Docker Hub")

    # commands (required)
    if 'commands' not in config:
        errors.append('Missing attribute \'commands\'')
    elif type(config['commands']) is not str:
        errors.append('Attribute \'commands\' must be a str')

    # mount
    if 'mount' in config:
        if type(config['mount']) is not list:
            errors.append('Attribute \'mount\' must be a list')
        elif config['mount'] is None or len(config['mount']) == 0:
            errors.append('Attribute \'mount\' must not be empty')

    # gpu
    if 'gpu' in config:
        if type(config['gpu']) is not bool:
            errors.append('Attribute \'mount\' must be a bool')

    # tags
    if 'tags' in config:
        if type(config['tags']) is not list:
            errors.append('Attribute \'tags\' must be a list')

    # legacy input format
    if 'from' in config:
        errors.append('Attribute \'from\' is deprecated; use an \'input\' section instead')

    # input
    if 'input' in config:
        # path
        if 'path' not in config['input']:
            errors.append('Missing attribute \'input.path\'')
        if config['input']['path'] != '' and config['input']['path'] is not None:
            cyverse_path_result = cyverse_path_exists(config['input']['path'], token)
            if type(cyverse_path_result) is bool and not cyverse_path_result:
                errors.append('Attribute \'input.path\' must be a str (either empty or a valid path in the CyVerse Data Store)')

        # kind
        if 'kind' not in config['input']:
            errors.append('Missing attribute \'input.kind\'')
        if not (config['input']['kind'] == 'file' or config['input']['kind'] == 'files' or config['input']['kind'] == 'directory'):
            errors.append('Attribute \'input.kind\' must be a string (either \'file\', \'files\', or \'directory\')')

        # legacy filetypes format
        if 'patterns' in config['input']:
            errors.append('Attribute \'input.patterns\' is deprecated; use \'input.filetypes\' instead')

        # filetypes
        if 'filetypes' in config['input']:
            if type(config['input']['filetypes']) is not list or not all(type(pattern) is str for pattern in config['input']['filetypes']):
                errors.append('Attribute \'input.filetypes\' must be a list of str')

    # legacy output format
    if 'to' in config:
        errors.append('Attribute \'to\' is deprecated; use an \'output\' section instead')

    # output
    if 'output' in config:
        # path
        if 'path' not in config['output']:
            errors.append('Attribute \'output\' must include attribute \'path\'')
        if config['output']['path'] is not None and type(config['output']['path']) is not str:
            errors.append('Attribute \'output.path\' must be a str')

        # include
        if 'include' in config['output']:
            if 'patterns' in config['output']['include']:
                if type(config['output']['include']['patterns']) is not list or not all(
                        type(pattern) is str for pattern in config['output']['include']['patterns']):
                    errors.append('Attribute \'output.include.patterns\' must be a list of str')
            if 'names' in config['output']['include']:
                if type(config['output']['include']['names']) is not list or not all(
                        type(name) is str for name in config['output']['include']['names']):
                    errors.append('Attribute \'output.include.names\' must be a list of str')

        # exclude
        if 'exclude' in config['output']:
            if 'patterns' in config['output']['exclude']:
                if type(config['output']['exclude']['patterns']) is not list or not all(
                        type(pattern) is str for pattern in config['output']['exclude']['patterns']):
                    errors.append('Attribute \'output.exclude.patterns\' must be a list of str')
            if 'names' in config['output']['exclude']:
                if type(config['output']['exclude']['names']) is not list or not all(
                        type(name) is str for name in config['output']['exclude']['names']):
                    errors.append('Attribute \'output.exclude.names\' must be a list of str')

    # doi (optional)
    if 'doi' in config:
        if type(config['doi']) is not str:
            errors.append('Attribute \'doi\' must be a str')

    return True if len(errors) == 0 else (False, errors)


def parse_bind_mount(workdir: str, bind_mount: str):
    split = bind_mount.rpartition(':')
    return BindMount(host_path=split[0], container_path=split[2]) if len(split) > 0 else BindMount(host_path=workdir, container_path=bind_mount)


def parse_run_options(raw: dict):
    errors = []

    image = None
    if not isinstance(raw['image'], str):
        errors.append('Attribute \'image\' must not be a str')
    elif raw['image'] == '':
        errors.append('Attribute \'image\' must not be empty')
    else:
        image = raw['image']
        if 'docker' in image:
            image_owner, image_name, image_tag = parse_docker_image_components(image)
            if not docker_image_exists(image_name, image_owner, image_tag):
                errors.append(f"Image '{image}' not found on Docker Hub")

    work_dir = None
    if not isinstance(raw['workdir'], str):
        errors.append('Attribute \'workdir\' must not be a str')
    elif raw['workdir'] == '':
        errors.append('Attribute \'workdir\' must not be empty')
    else:
        work_dir = raw['workdir']

    command = None
    if not isinstance(raw['command'], str):
        errors.append('Attribute \'command\' must not be a str')
    elif raw['command'] == '':
        errors.append('Attribute \'command\' must not be empty')
    else:
        command = raw['command']

    parameters = None
    if 'parameters' in raw:
        if not all(['key' in param and
                    param['key'] is not None and
                    param['key'] != '' and
                    'value' in param and
                    param['value'] is not None and
                    param['value'] != ''
                    for param in raw['parameters']]):
            errors.append('Every parameter must have a non-empty \'key\' and \'value\'')
        else:
            parameters = [Parameter(param['key'], param['value']) for param in raw['parameters']]

    bind_mounts = None
    if 'bind_mounts' in raw:
        if not all (mount_point != '' for mount_point in raw['bind_mounts']):
            errors.append('Every mount point must be non-empty')
        else:
            bind_mounts = [parse_bind_mount(work_dir, mount_point) for mount_point in raw['bind_mounts']]

    input = None
    if 'input' in raw:
        if 'file' in raw['input']:
            if 'path' not in raw['input']['file']:
                errors.append('Section \'file\' must include attribute \'path\'')
            input = FileInput(path=raw['input']['file']['path'])
        elif 'files' in raw['input']:
            if 'path' not in raw['input']['files']:
                errors.append('Section \'files\' must include attribute \'path\'')
            input = FilesInput(
                path=raw['input']['files']['path'],
                patterns=raw['input']['files']['patterns'] if 'patterns' in raw['input']['files'] else None)
        elif 'directory' in raw['input']:
            if 'path' not in raw['input']['directory']:
                errors.append('Section \'directory\' must include attribute \'path\'')
            input = DirectoryInput(path=raw['input']['directory']['path'])
        else:
            errors.append('Section \'input\' must include a \'file\', \'files\', or \'directory\' section')

    log_file = None
    if 'log_file' in raw:
        log_file = raw['log_file']
        if not isinstance(log_file, str):
            errors.append('Attribute \'log_file\' must be a str')
        elif log_file.rpartition('/')[0] != '' and not isdir(log_file.rpartition('/')[0]):
            errors.append('Attribute \'log_file\' must be a valid file path')

    no_cache = None
    if 'no_cache' in raw:
        no_cache = raw['no_cache']
        if not isinstance(no_cache, bool):
            errors.append('Attribute \'no_cache\' must be a bool')

    gpu = None
    if 'gpu' in raw:
        gpu = raw['gpu']
        if not isinstance(gpu, bool):
            errors.append('Attribute \'gpu\' must be a bool')

    jobqueue = None
    if 'jobqueue' in raw:
        jobqueue = raw['jobqueue']
        if not ('slurm' in jobqueue or 'yarn' in jobqueue or 'pbs' in jobqueue or 'moab' in jobqueue or 'sge' in jobqueue or 'lsf' in jobqueue or 'oar' in jobqueue or 'kube' in jobqueue):
            raise ValueError(f"Unsupported jobqueue configuration: {jobqueue}")

        if 'queue' in jobqueue:
            if not isinstance(jobqueue['queue'], str):
                errors.append('Section \'jobqueue\'.\'queue\' must be a str')
        if 'project' in jobqueue:
            if not isinstance(jobqueue['project'], str):
                errors.append('Section \'jobqueue\'.\'project\' must be a str')
        if 'walltime' in jobqueue:
            if not isinstance(jobqueue['walltime'], str):
                errors.append('Section \'jobqueue\'.\'walltime\' must be a str')
        if 'cores' in jobqueue:
            if not isinstance(jobqueue['cores'], int):
                errors.append('Section \'jobqueue\'.\'cores\' must be a int')
        if 'processes' in jobqueue:
            if not isinstance(jobqueue['processes'], int):
                errors.append('Section \'jobqueue\'.\'processes\' must be a int')
        if 'extra' in jobqueue and not all(extra is str for extra in jobqueue['extra']):
            errors.append('Section \'jobqueue\'.\'extra\' must be a list of str')
        if 'header_skip' in jobqueue and not all(extra is str for extra in jobqueue['header_skip']):
            errors.append('Section \'jobqueue\'.\'header_skip\' must be a list of str')

    return errors, RunOptions(
        workdir=work_dir,
        image=image,
        command=command,
        input=input,
        parameters=parameters,
        bind_mounts=bind_mounts,
        # checksums=checksums,
        log_file=log_file,
        jobqueue=jobqueue,
        no_cache=no_cache,
        gpu=gpu)


def format_bind_mount(workdir: str, bind_mount: BindMount):
    return bind_mount.host_path + ':' + bind_mount.container_path if bind_mount.host_path != '' else workdir + ':' + bind_mount.container_path


def prep_run_command(
        work_dir: str,
        image: str,
        command: str,
        bind_mounts: List[BindMount] = None,
        parameters: List[Parameter] = None,
        docker_username: str = None,
        docker_password: str = None,
        no_cache: bool = False,
        gpu: bool = False):
    cmd = f"singularity exec --home {work_dir}"

    if bind_mounts is not None:
        if len(bind_mounts) > 0:
            cmd += (' --bind ' + ','.join([format_bind_mount(work_dir, mount_point) for mount_point in bind_mounts]))
        else:
            raise ValueError(f"List expected for `bind_mounts`")

    if parameters is None:
        parameters = []
    parameters.append(Parameter(key='WORKDIR', value=work_dir))
    for parameter in parameters:
        print(f"Replacing '{parameter.key.upper()}' with '{parameter.value}'")
        command = command.replace(f"${parameter.key.upper()}", parameter.value)

    if no_cache:
        cmd += ' --disable-cache'

    if gpu:
        cmd += ' --nv'

    cmd += f" {image} {command}"
    print(f"Using command: '{cmd}'")

    # we don't necessarily want to reveal Docker auth info to the end user, so print the command before adding Docker env variables
    if docker_username is not None and docker_password is not None:
        cmd = f"SINGULARITY_DOCKER_USERNAME={docker_username} SINGULARITY_DOCKER_PASSWORD={docker_password} " + cmd

    return cmd


def get_csrf_token(request):
    token = request.session.get('csrfToken', None)
    if token is None:
        token = generate_secret_key()
        request.session['csrfToken'] = token
    return token


def generate_random_string(length, allowed_chars='abcdefghijklmnopqrstuvwxyz' 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    return ''.join(choice(allowed_chars) for i in range(length))


def generate_secret_key():
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return generate_random_string(40, chars)
