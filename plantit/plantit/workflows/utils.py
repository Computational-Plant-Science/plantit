import asyncio
from os.path import join
from typing import List

import httpx
import requests
from requests import Response

from plantit.docker import parse_image_components, image_exists
from plantit.runs.models import Run
from plantit.github import get_repo_config, get_repo_readme
from plantit.terrain import path_exists


def refresh_workflow(username: str, name: str, token: str) -> dict:
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
    }

    with httpx.Client(headers=headers) as client:
        response = client.get(f"https://api.github.com/repos/{username}/{name}")
        repo = response.json()
        owner = repo['owner']['login']
        name = repo['name']
        return {
            'repo': repo,
            'config': get_repo_config(name, owner, token),
            # 'readme': get_repo_readme(name, owner, token)
        }


async def list_workflows_for_users(usernames: List[str], token: str) -> List[dict]:
    urls = [f"https://api.github.com/search/code?q=filename:plantit.yaml+user:{username}" for username in usernames]
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
    }

    async with httpx.AsyncClient(headers=headers) as client:
        futures = [client.get(url) for url in urls]
        responses = await asyncio.gather(*futures)
        return [workflow for workflows in [format_workflows(response, token) for response in responses] for workflow in workflows]


def list_workflows_for_user(username: str, token: str) -> List[dict]:
    response = requests.get(
        f"https://api.github.com/search/code?q=filename:plantit.yaml+user:{username}",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
        })
    workflows = format_workflows(response, token)
    return [workflow for workflow in workflows]


def search_workflows_by_name(username: str, name: str, token: str) -> dict:
    repo = requests.get(
        f"https://api.github.com/repos/{username}/{name}",
        headers={
            "Authorization": f"token {token}",
        }).json()
    if 'message' in repo and repo['message'] == 'Not Found': return None
    config = get_repo_config(repo['name'], repo['owner']['login'], token)
    result = validate_workflow_config(config, token)
    if isinstance(result, bool):
        return {
            'repo': repo,
            'config': config,
            'validation': {
                'is_valid': True,
                'errors': []
            }
        }
    else:
        return {
            'repo': repo,
            'config': config,
            'validation': {
                'is_valid': result[0],
                'errors': result[1]
            }
        }


def map_old_workflow_config_to_new(old: dict, run: Run, resources: dict) -> dict:
    new_config = {
        'image': old['config']['image'],
        'command': old['config']['commands'],
        'workdir': old['config']['workdir'],
        'log_file': f"{run.guid}.{run.agent.name.lower()}.log"
    }

    del old['config']['agent']

    if 'mount' in old['config']:
        new_config['bind_mounts'] = old['config']['mount']

    if 'parameters' in old['config']:
        old_params = old['config']['parameters']
        params = []
        for p in old_params:
            if p['type'] == 'string':
                params.append({
                    'key': p['name'],
                    'value': str(p['value'])
                })
            elif p['type'] == 'select':
                params.append({
                    'key': p['name'],
                    'value': str(p['value'])
                })
            elif p['type'] == 'number':
                params.append({
                    'key': p['name'],
                    'value': str(p['value'])
                })
            elif p['type'] == 'boolean':
                params.append({
                    'key': p['name'],
                    'value': str(p['value'])
                })
        new_config['parameters'] = params

    if 'input' in old['config']:
        input_kind = old['config']['input']['kind'] if 'kind' in old['config']['input'] else None
        new_config['input'] = dict()
        if input_kind == 'directory':
            new_config['input']['directory'] = dict()
            new_config['input']['directory']['path'] = join(run.agent.workdir, run.workdir, 'input')
            new_config['input']['directory']['patterns'] = old['config']['input']['patterns']
        elif input_kind == 'files':
            new_config['input']['files'] = dict()
            new_config['input']['files']['path'] = join(run.agent.workdir, run.workdir, 'input')
            new_config['input']['files']['patterns'] = old['config']['input']['patterns']
        elif input_kind == 'file':
            new_config['input']['file'] = dict()
            new_config['input']['file']['path'] = join(run.agent.workdir, run.workdir, 'input',
                                                       old['config']['input']['from'].rpartition('/')[2])

    sandbox = run.agent.name == 'Sandbox'
    work_dir = join(run.agent.workdir, run.workdir)
    if not sandbox and not run.agent.job_array:
        new_config['jobqueue'] = dict()
        new_config['jobqueue']['slurm'] = {
            'cores': resources['cores'],
            'processes': resources['processes'],
            'walltime': resources['time'],
            'local_directory': work_dir,
            'log_directory': work_dir,
            'env_extra': [run.agent.pre_commands]
        }

        if 'mem' in resources:
            new_config['jobqueue']['slurm']['memory'] = resources['mem']
        if run.agent.queue is not None and run.agent.queue != '':
            new_config['jobqueue']['slurm']['queue'] = run.agent.queue
        if run.agent.project is not None and run.agent.project != '':
            new_config['jobqueue']['slurm']['project'] = run.agent.project
        if run.agent.header_skip is not None and run.agent.header_skip != '':
            new_config['jobqueue']['slurm']['header_skip'] = run.agent.header_skip.split(',')

        if 'gpu' in old['config'] and old['config']['gpu']:
            if run.agent.gpu:
                print(f"Using GPU on {run.agent.name} queue '{run.agent.gpu_queue}'")
                new_config['gpu'] = True
                new_config['jobqueue']['slurm']['job_extra'] = [f"--gres=gpu:1"]
                new_config['jobqueue']['slurm']['queue'] = run.agent.gpu_queue
            else:
                print(f"No GPU support on {run.agent.name}")

    return new_config


def format_workflows(response: Response, token: str) -> List[dict]:
    response_json = response.json()
    workflows = [{
        'repo': item['repository'],
        'config': get_repo_config(item['repository']['name'], item['repository']['owner']['login'], token),
        # 'readme': get_repo_readme(item['repository']['name'], item['repository']['owner']['login'], token)
    } for item in response_json['items']] if 'items' in response_json else []
    return workflows


def validate_workflow_config(config, token):
    errors = []

    # name (required)
    if 'name' not in config:
        errors.append('Missing attribute \'name\'')
    elif type(config['name']) is not str:
        errors.append('Attribute \'name\' must be a str')

    # author (optional)
    if 'author' in config:
        author = config['author']
        if (type(author) is str and author == '') or (type(author) is list and not all(type(d) is str for d in author)):
            errors.append('Attribute \'author\' must be a non-empty str or list of str')

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
        image_owner, image_name, image_tag = parse_image_components(config['image'])
        if 'docker' in config['image'] and not image_exists(image_name, image_owner, image_tag):
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
            cyverse_path_result = path_exists(config['input']['path'], token)
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
        doi = config['doi']
        if (type(doi) is str and doi == '') or (type(doi) is list and not all(type(d) is str for d in doi)):
            errors.append('Attribute \'doi\' must be a non-empty str or list of str')

    return True if len(errors) == 0 else (False, errors)