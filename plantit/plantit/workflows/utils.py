import asyncio
import json
import logging
from datetime import datetime
from os.path import join
from typing import List

from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone

from plantit.github import get_repo, list_connectable_repos_by_owner
from plantit.redis import RedisClient
from plantit.tasks.models import Task
from plantit.workflows.models import Workflow

logger = logging.getLogger(__name__)


def map_old_workflow_config_to_new(old: dict, run: Task, resources: dict) -> dict:
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


async def bind_workflow(workflow: Workflow, token: str) -> dict:
    repo = await get_repo(
        workflow.repo_owner,
        workflow.repo_name,
        token)
    return {
        'config': repo['config'],
        'repo': repo['repo'],
        'validation': repo['validation'],
        'public': workflow.public,
        'connected': True
    }


async def repopulate_personal_workflow_cache(owner: str):
    try:
        user = User.objects.get(profile__github_username=owner)
    except:
        logger.warning(f"User {owner} does not exist")
        return

    empty_personal_workflow_cache(owner)

    owned = list(Workflow.objects.filter(user=user))
    bind = asyncio.gather(*[bind_workflow(workflow, user.profile.github_token) for workflow in owned])
    results = await asyncio.gather(*[bind, list_connectable_repos_by_owner(owner, user.profile.github_token)])
    connected = results[0]
    connectable = results[1]
    both = []

    for able in connectable:
        if not any(['name' in ed['config'] and 'name' in able['config'] and ed['config']['name'] == able['config']['name'] for ed in connected]):
            able['public'] = False
            able['connected'] = False
            both.append(able)

    missing = 0
    for ed in [c for c in connected if c['repo']['owner']['login'] == owner]:  # omit manually added workflows (e.g., owned by a GitHub Organization)
        name = ed['config']['name']
        if not any(['name' in able['config'] and able['config']['name'] == name for able in connectable]):
            missing += 1
            logger.warning(f"Configuration file missing for {owner}'s workflow {name}")
            ed['validation'] = {
                'is_valid': False,
                'errors': ["Configuration file missing"]
            }
        both.append(ed)

    redis = RedisClient.get()
    for workflow in both: redis.set(f"workflows/{owner}/{workflow['repo']['name']}", json.dumps(workflow))
    redis.set(f"workflows_updated/{owner}", timezone.now().timestamp())
    logger.info(f"Added {len(connected)} connected, {len(connectable) - len(connected)} connectable, {len(both)} total to {owner}'s workflow cache" + ("" if missing == 0 else f"({missing} with missing configuration files)"))


async def repopulate_public_workflow_cache():
    redis = RedisClient.get()
    users = [workflow.user for workflow in list(Workflow.objects.filter(public=True))]  # only include users with public workflows

    for user in users:
        empty_personal_workflow_cache(user.profile.github_username)
        await repopulate_personal_workflow_cache(user.profile.github_username)

    redis.set(f"public_workflows_updated", timezone.now().timestamp())


async def get_public_workflows(invalidate: bool = False) -> List[dict]:
    redis = RedisClient.get()
    updated = redis.get('public_workflows_updated')

    # repopulate if empty or invalidation requested
    if updated is None or len(list(redis.scan_iter(match=f"workflows/*"))) == 0 or invalidate:
        await repopulate_public_workflow_cache()
    else:
        age = (datetime.now() - datetime.fromtimestamp(float(updated)))
        age_secs = age.total_seconds()
        max_secs = (int(settings.WORKFLOWS_REFRESH_MINUTES) * 60)

        # otherwise only if stale
        if age_secs > max_secs:
            logger.info(f"Public workflow cache is stale ({age_secs}s old, {age_secs - max_secs}s past limit), repopulating")
            await repopulate_public_workflow_cache()

    workflows = [json.loads(redis.get(key)) for key in redis.scan_iter(match='workflows/*')]
    return [workflow for workflow in workflows if workflow['public']]


async def get_personal_workflows(owner: str, invalidate: bool = False) -> List[dict]:
    redis = RedisClient.get()
    updated = redis.get(f"workflows_updated/{owner}")

    # repopulate if empty or invalidation requested
    if updated is None or len(list(redis.scan_iter(match=f"workflows/{owner}/*"))) == 0 or invalidate:
        await repopulate_personal_workflow_cache(owner)
    else:
        age = (datetime.now() - datetime.fromtimestamp(float(updated)))
        age_secs = age.total_seconds()
        max_secs = (int(settings.WORKFLOWS_REFRESH_MINUTES) * 60)

        # otherwise only if stale
        if age_secs > max_secs:
            logger.info(f"GitHub user {owner}'s workflow cache is stale ({age_secs}s old, {age_secs - max_secs}s past limit), repopulating")
            await repopulate_personal_workflow_cache(owner)

    return [json.loads(redis.get(key)) for key in redis.scan_iter(match=f"workflows/{owner}/*")]


async def get_workflow(owner: str, name: str, token: str, invalidate: bool = False) -> dict:
    redis = RedisClient.get()
    updated = redis.get(f"workflows_updated/{owner}")
    workflow = redis.get(f"workflows/{owner}/{name}")

    if updated is None or workflow is None or invalidate:
        try: workflow = Workflow.objects.get(repo_owner=owner, repo_name=name)
        except: raise ValueError(f"Workflow {owner}/{name} not found")

        workflow = await bind_workflow(workflow, token)
        redis.set(f"workflows/{owner}/{name}", json.dumps(workflow))

    return workflow


def empty_personal_workflow_cache(owner: str):
    redis = RedisClient.get()
    keys = list(redis.scan_iter(match=f"workflows/{owner}/*"))
    cleaned = len(keys)
    for key in keys: redis.delete(key)
    logger.info(f"Emptied {cleaned} workflows from GitHub user {owner}'s cache")
    return cleaned
