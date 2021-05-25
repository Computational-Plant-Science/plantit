import asyncio
import binascii
import fileinput
import json
import os
import re
import sys
import uuid
from datetime import timedelta, datetime
from math import ceil
from os import environ
from os.path import join
from pathlib import Path
from typing import List

import httpx
import requests
import yaml
from asgiref.sync import async_to_sync
from celery.utils.log import get_task_logger
from channels.layers import get_channel_layer
from dateutil import parser
from django.contrib.auth.models import User
from django.utils import timezone
from requests import RequestException, ReadTimeout, Timeout, HTTPError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from plantit import settings
from plantit.options import FileInput, Parameter
from plantit.redis import RedisClient
from plantit.agents.models import Agent, AgentAccessPolicy, AgentRole
from plantit.agents.utils import map_agent
from plantit.runs.models import Run, DelayedRunTask, RepeatingRunTask
from plantit.runs.ssh import SSH
from plantit.utils import get_repo_config, parse_run_options, prep_run_command

logger = get_task_logger(__name__)


def clean_html(raw_html):
    expr = re.compile('<.*?>')
    text = re.sub(expr, '', raw_html)
    return text


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type())
def execute_command(ssh_client: SSH, pre_command: str, command: str, directory: str, allow_stderr: bool = False) -> List[str]:
    full_command = f"{pre_command} && cd {directory} && {command}" if directory else command
    output = []
    errors = []

    print(f"Executing command on '{ssh_client.host}': {full_command}")
    stdin, stdout, stderr = ssh_client.client.exec_command(full_command, get_pty=True)
    stdin.close()

    for line in iter(lambda: stdout.readline(2048), ""):
        clean = clean_html(line)
        output.append(clean)
        print(f"Received stdout from '{ssh_client.host}': '{clean}'")
    for line in iter(lambda: stderr.readline(2048), ""):
        clean = clean_html(line)
        if 'WARNING' not in clean:  # Dask occasionally returns messages like 'distributed.worker - WARNING - Heartbeat to scheduler failed'
            errors.append(clean)
            print(f"Received stderr from '{ssh_client.host}': '{clean}'")
    if stdout.channel.recv_exit_status() != 0:
        raise Exception(f"Received non-zero exit status from '{ssh_client.host}'")
    elif not allow_stderr and len(errors) > 0:
        raise Exception(f"Received stderr: {errors}")

    return output


def update_status(run: Run, description: str):
    log_path = join(environ.get('RUNS_LOGS'), f"{run.guid}.plantit.log")
    with open(log_path, 'a') as log:
        log.write(f"{description}\n")

    async_to_sync(get_channel_layer().group_send)(f"runs-{run.user.username}", {
        'type': 'update_status',
        'run': map_run(run),
    })


def stat_logs(id: str):
    log_path = Path(join(environ.get('RUNS_LOGS'), f"{id}.plantit.log"))
    return datetime.fromtimestamp(log_path.stat().st_mtime) if log_path.is_file() else None


def remove_logs(id: str, agent: str):
    local_log_path = join(environ.get('RUNS_LOGS'), f"{id}.plantit.log")
    # agent_log_path = join(environ.get('RUNS_LOGS'), f"{id}.{agent.lower()}.log")
    os.remove(local_log_path)
    # os.remove(agent_log_path)


def format_workflows(response, token):
    response_json = response.json()
    workflows = [{
        'repo': item['repository'],
        'config': get_repo_config(item['repository']['name'], item['repository']['owner']['login'], token),
        # 'readme': get_repo_readme(item['repository']['name'], item['repository']['owner']['login'], token)
    } for item in response_json['items']] if 'items' in response_json else []
    return workflows


async def list_workflows_for_users(usernames: List[str], token: str):
    urls = [f"https://api.github.com/search/code?q=filename:plantit.yaml+user:{username}" for username in usernames]
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
    }

    async with httpx.AsyncClient(headers=headers) as client:
        futures = [client.get(url) for url in urls]
        responses = await asyncio.gather(*futures)
        return [workflow for workflows in [format_workflows(response, token) for response in responses] for workflow in workflows]


def list_workflows_for_user(username: str, token: str):
    response = requests.get(
        f"https://api.github.com/search/code?q=filename:plantit.yaml+user:{username}",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.mercy-preview+json"  # so repo topics will be returned
        })
    workflows = format_workflows(response, token)
    return [flow for flow in workflows]


def map_old_workflow_config_to_new(old_config: dict, run: Run, resources: dict):
    new_config = {
        'image': old_config['config']['image'],
        'command': old_config['config']['commands'],
        'workdir': old_config['config']['workdir'],
        'log_file': f"{run.guid}.{run.agent.name.lower()}.log"
    }

    del old_config['config']['agent']

    if 'mount' in old_config['config']:
        new_config['bind_mounts'] = old_config['config']['mount']

    if 'parameters' in old_config['config']:
        old_params = old_config['config']['parameters']
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

    if 'input' in old_config['config']:
        input_kind = old_config['config']['input']['kind'] if 'kind' in old_config['config']['input'] else None
        new_config['input'] = dict()
        if input_kind == 'directory':
            new_config['input']['directory'] = dict()
            new_config['input']['directory']['path'] = join(run.agent.workdir, run.workdir, 'input')
            new_config['input']['directory']['patterns'] = old_config['config']['input']['patterns']
        elif input_kind == 'files':
            new_config['input']['files'] = dict()
            new_config['input']['files']['path'] = join(run.agent.workdir, run.workdir, 'input')
            new_config['input']['files']['patterns'] = old_config['config']['input']['patterns']
        elif input_kind == 'file':
            new_config['input']['file'] = dict()
            new_config['input']['file']['path'] = join(run.agent.workdir, run.workdir, 'input',
                                                       old_config['config']['input']['from'].rpartition('/')[2])

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

        if 'gpu' in old_config['config'] and old_config['config']['gpu']:
            if run.agent.gpu:
                print(f"Using GPU on {run.agent.name} queue '{run.agent.gpu_queue}'")
                new_config['gpu'] = True
                new_config['jobqueue']['slurm']['job_extra'] = [f"--gres=gpu:1"]
                new_config['jobqueue']['slurm']['queue'] = run.agent.gpu_queue
            else:
                print(f"No GPU support on {run.agent.name}")

    return new_config


def parse_walltime(walltime) -> timedelta:
    time_split = walltime.split(':')
    time_hours = int(time_split[0])
    time_minutes = int(time_split[1])
    time_seconds = int(time_split[2])
    return timedelta(hours=time_hours, minutes=time_minutes, seconds=time_seconds)


def parse_job_id(line: str) -> str:
    try:
        return str(int(line.replace('Submitted batch job', '').strip()))
    except:
        raise Exception(f"Failed to parse job ID from: '{line}'")


def map_run_task(task):
    return {
        'name': task.name,
        'run': map_run(task.run),
        # 'crontab': task.crontab if task.crontab is not None else None,
        'interval': {
            'every': task.interval.every,
            'period': task.interval.period
        } if task.interval is not None else None,
        'enabled': task.enabled,
        'last_run': task.last_run_at
    }


def map_run(run: Run):
    submission_log_file = submission_log_file_path(run)

    if Path(submission_log_file).is_file():
        with open(submission_log_file, 'r') as log:
            submission_logs = [line.strip() for line in log.readlines()[-int(1000000):]]
    else:
        submission_logs = []

    try:
        AgentAccessPolicy.objects.get(user=run.user, agent=run.agent, role__in=[AgentRole.own, AgentRole.run])
        can_restart = True
    except:
        can_restart = False

    results = RedisClient.get().get(f"results/{run.guid}")

    return {
        'can_restart': can_restart,
        'id': run.guid,
        'job_id': run.job_id,
        'job_status': run.job_status,
        'job_walltime': run.job_elapsed_walltime,
        'work_dir': run.workdir,
        'submission_logs': submission_logs,
        'agent': run.agent.name,
        'created': run.created.isoformat(),
        'updated': run.updated.isoformat(),
        'completed': run.completed.isoformat() if run.completed is not None else None,
        'workflow_owner': run.workflow_owner,
        'workflow_name': run.workflow_name,
        'tags': [str(tag) for tag in run.tags.all()],
        'is_complete': run.is_complete,
        'is_success': run.is_success,
        'is_failure': run.is_failure,
        'is_cancelled': run.is_cancelled,
        'is_timeout': run.is_timeout,
        'workflow_image_url': run.workflow_image_url,
        'result_previews_loaded': run.previews_loaded,
        'cleaned_up': run.cleaned_up,
        'output_files': json.loads(results) if results is not None else None
    }


def submission_log_file_path(run: Run):
    return join(os.environ.get('RUNS_LOGS'), f"{run.guid}.plantit.log")


def container_log_file_name(run: Run):
    if run.agent.launcher:
        return f"plantit.{run.job_id}.out"
    else:
        return f"{run.guid}.{run.agent.name.lower()}.log"


def container_log_file_path(run: Run):
    return join(os.environ.get('RUNS_LOGS'), container_log_file_name(run))


def create_run(username: str, agent_name: str, workflow: dict) -> Run:
    now = timezone.now()
    user = User.objects.get(username=username)
    agent = Agent.objects.get(name=agent_name)
    workflow_owner = workflow['repo']['owner']['login']
    workflow_name = workflow['repo']['name']
    workflow_config = get_repo_config(workflow_name, workflow_owner, user.profile.github_token)
    run = Run.objects.create(
        guid=str(uuid.uuid4()),
        user=user,
        workflow_owner=workflow_owner,
        workflow_name=workflow_name,
        agent=agent,
        job_status='CREATED',
        created=now,
        updated=now,
        token=binascii.hexlify(os.urandom(20)).decode())

    if 'logo' in workflow_config:
        run.workflow_image_url = f"https://raw.githubusercontent.com/{workflow_owner}/{workflow_name}/master/{workflow_config['logo']}"

    # add tags
    for tag in workflow['config']['tags']:
        run.tags.add(tag)

    # guid for working directory name
    run.workdir = f"{run.guid}/"
    run.save()
    return run


def parse_time(data: dict) -> datetime:
    time_str = data['time']
    time = parser.isoparse(time_str)
    return time


def parse_eta(data: dict) -> (datetime, int):
    delay_value = data['delayValue']
    delay_units = data['delayUnits']

    if delay_units == 'Seconds':
        seconds = int(delay_value)
    elif delay_units == 'Minutes':
        seconds = int(delay_value) * 60
    elif delay_units == 'Hours':
        seconds = int(delay_value) * 60 * 60
    elif delay_units == 'Days':
        seconds = int(delay_value) * 60 * 60 * 24
    else:
        raise ValueError(f"Unsupported delay units (expected: Seconds, Minutes, Hours, or Days)")

    now = timezone.now()
    eta = now + timedelta(seconds=seconds)

    return eta, seconds


def map_delayed_run_task(task: DelayedRunTask):
    return {
        'agent': map_agent(task.agent),
        'name': task.name,
        'eta': task.eta,
        'interval': {
            'every': task.interval.every,
            'period': task.interval.period
        },
        'last_run': task.last_run_at
    }


def map_repeating_run_task(task: RepeatingRunTask):
    return {
        'agent': map_agent(task.agent),
        'name': task.name,
        'eta': task.eta,
        'interval': {
            'every': task.interval.every,
            'period': task.interval.period
        },
        'enabled': task.enabled,
        'last_run': task.last_run_at
    }


def get_run_results(run: Run, workflow: dict):
    included_by_name = ((workflow['output']['include']['names'] if 'names' in workflow['output'][
        'include'] else [])) if 'output' in workflow else []  # [f"{run.task_id}.zip"]
    included_by_name.append(f"{run.guid}.zip")  # zip file
    if not run.agent.launcher:
        included_by_name.append(f"{run.guid}.{run.agent.name.lower()}.log")
    if run.job_id is not None and run.job_id != '':
        included_by_name.append(f"plantit.{run.job_id}.out")
        included_by_name.append(f"plantit.{run.job_id}.err")
    included_by_pattern = (
        workflow['output']['include']['patterns'] if 'patterns' in workflow['output']['include'] else []) if 'output' in workflow else []

    client = SSH(run.agent.hostname, run.agent.port, run.agent.username)
    work_dir = join(run.agent.workdir, run.workdir)
    outputs = []
    seen = []

    with client:
        with client.client.open_sftp() as sftp:
            for file in included_by_name:
                file_path = join(work_dir, file)
                stdin, stdout, stderr = client.client.exec_command(f"test -e {file_path} && echo exists")
                output = {
                    'name': file,
                    'path': join(work_dir, file),
                    'exists': stdout.read().decode().strip() == 'exists'
                }
                seen.append(output['name'])
                outputs.append(output)

            for f in sftp.listdir(work_dir):
                if any(pattern in f for pattern in included_by_pattern):
                    if not any(s == f for s in seen):
                        outputs.append({
                            'name': f,
                            'path': join(work_dir, f),
                            'exists': True
                        })

    return outputs


def get_job_walltime(run: Run) -> (str, str):
    ssh = SSH(run.agent.hostname, run.agent.port, run.agent.username)
    with ssh:
        lines = execute_command(
            ssh_client=ssh,
            pre_command=":",
            command=f"squeue --user={run.agent.username}",
            directory=join(run.agent.workdir, run.workdir),
            allow_stderr=True)

        try:
            job_line = next(l for l in lines if run.job_id in l)
            job_split = job_line.split()
            job_walltime = job_split[-3]
            return job_walltime
        except StopIteration:
            return None


def get_job_status(run: Run) -> str:
    ssh = SSH(run.agent.hostname, run.agent.port, run.agent.username)
    with ssh:
        lines = execute_command(
            ssh_client=ssh,
            pre_command=':',
            command=f"sacct -j {run.job_id}",
            directory=join(run.agent.workdir, run.workdir),
            allow_stderr=True)

        job_line = next(l for l in lines if run.job_id in l)
        job_split = job_line.split()
        job_status = job_split[5].replace('+', '')
        return job_status
    pass


def cancel_run(run: Run):
    ssh = SSH(run.agent.hostname, run.agent.port, run.agent.username)
    with ssh:
        if run.job_id is None or not any([run.job_id in r for r in execute_command(
                ssh_client=ssh,
                pre_command=':',
                command=f"squeue -u {run.agent.username}",
                directory=join(run.agent.workdir, run.workdir))]):
            # run doesn't exist, so no need to cancel
            return

        execute_command(
            ssh_client=ssh,
            pre_command=':',
            command=f"scancel {run.job_id}",
            directory=join(run.agent.workdir, run.workdir))


def submit_run_via_ssh(flow, run: Run, ssh: SSH, file_count: int = None):
    # TODO refactor to allow multiple schedulers
    sandbox = run.agent.name == 'Sandbox'  # for now, we're either in the sandbox or on a SLURM cluster
    template = environ.get('CELERY_TEMPLATE_LOCAL_RUN_SCRIPT') if sandbox else environ.get('CELERY_TEMPLATE_SLURM_RUN_SCRIPT')
    template_name = template.split('/')[-1]

    if run.is_sandbox:
        execute_command(
            ssh_client=ssh,
            pre_command='; '.join(str(run.agent.pre_commands).splitlines()) if run.agent.pre_commands else ':',
            command=f"chmod +x {template_name} && ./{template_name}",
            directory=join(run.agent.workdir, run.workdir),
            allow_stderr=True)

        # get container logs
        work_dir = join(run.agent.workdir, run.workdir)
        ssh_client = SSH(run.agent.hostname, run.agent.port, run.agent.username)
        container_log_file = container_log_file_name(run)
        container_log_path = container_log_file_path(run)

        with ssh_client:
            with ssh_client.client.open_sftp() as sftp:
                cmd = 'test -e {0} && echo exists'.format(join(work_dir, container_log_file))
                stdin, stdout, stderr = ssh_client.client.exec_command(cmd)

                if not stdout.read().decode().strip() == 'exists':
                    container_logs = []
                else:
                    with open(container_log_file_path(run), 'a+') as log_file:
                        sftp.chdir(work_dir)
                        sftp.get(container_log_file, log_file.name)

                    # obfuscate Docker auth info before returning logs to the user
                    docker_username = environ.get('DOCKER_USERNAME', None)
                    docker_password = environ.get('DOCKER_PASSWORD', None)
                    for line in fileinput.input([container_log_path], inplace=True):
                        if docker_username in line.strip():
                            line = line.strip().replace(docker_username, '*' * 7, 1)
                        if docker_password in line.strip():
                            line = line.strip().replace(docker_password, '*' * 7)
                        sys.stdout.write(line)
    else:
        command = f"sbatch {template_name}"
        output_lines = execute_command(
            ssh_client=ssh,
            pre_command='; '.join(str(run.agent.pre_commands).splitlines()) if run.agent.pre_commands else ':',
            # if the scheduler prohibits nested job submissions, we need to run the CLI from a login node
            command=command,
            directory=join(run.agent.workdir, run.workdir),
            allow_stderr=True)
        job_id = parse_job_id(output_lines[-1])
        run.job_id = job_id
        run.updated = timezone.now()
        run.save()


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
def list_dir(path: str, token: str) -> List[str]:
    with requests.get(
            f"https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path={path}",
            headers={'Authorization': f"Bearer {token}"}) as response:
        if response.status_code == 500 and response.json()['error_code'] == 'ERR_DOES_NOT_EXIST':
            raise ValueError(f"Path {path} does not exist")

        response.raise_for_status()
        content = response.json()
        files = content['files']
        return [file['path'] for file in files]


def upload_run(workflow: dict, run: Run, ssh: SSH, input_files: List[str] = None):
    # update flow config before uploading
    workflow['config']['workdir'] = join(run.agent.workdir, run.guid)
    workflow['config']['log_file'] = f"{run.guid}.{run.agent.name.lower()}.log"
    if 'output' in workflow['config'] and 'from' in workflow['config']['output']:
        if workflow['config']['output']['from'] is not None and workflow['config']['output']['from'] != '':
            workflow['config']['output']['from'] = join(run.agent.workdir, run.workdir, workflow['config']['output']['from'])

    # if flow has outputs, make sure we don't push configuration or job scripts
    if 'output' in workflow['config']:
        workflow['config']['output']['exclude']['names'] = [
            "flow.yaml",
            "template_local_run.sh",
            "template_slurm_run.sh"]

    resources = None if 'resources' not in workflow['config']['agent'] else workflow['config']['agent']['resources']
    callback_url = settings.API_URL + 'runs/' + run.guid + '/status/'
    work_dir = join(run.agent.workdir, run.workdir)
    new_flow = map_old_workflow_config_to_new(workflow, run, resources)  # TODO update flow UI page
    launcher = run.agent.launcher  # whether to use TACC launcher

    parse_errors, run_options = parse_run_options(new_flow)
    if len(parse_errors) > 0:
        raise ValueError(f"Failed to parse run options: {' '.join(parse_errors)}")

    # create working directory
    execute_command(ssh_client=ssh, pre_command=':', command=f"mkdir {work_dir}", directory=run.agent.workdir, allow_stderr=True)

    # upload flow config and job script
    with ssh.client.open_sftp() as sftp:
        sftp.chdir(work_dir)

        # TODO refactor to allow multiple schedulers
        sandbox = run.agent.name == 'Sandbox'  # for now, we're either in the sandbox or on a SLURM cluster
        template = environ.get('CELERY_TEMPLATE_LOCAL_RUN_SCRIPT') if sandbox else environ.get('CELERY_TEMPLATE_SLURM_RUN_SCRIPT')
        template_name = template.split('/')[-1]

        # upload flow config file
        with sftp.open('flow.yaml', 'w') as flow_file:
            if launcher:
                del new_flow['jobqueue']
            yaml.dump(new_flow, flow_file, default_flow_style=False)

        # compose and upload job script
        with open(template, 'r') as template_script, sftp.open(template_name, 'w') as script:
            print(f"Uploading {template_name}")
            for line in template_script:
                script.write(line)

            if not sandbox:
                # we're on a SLURM cluster, so add resource requests
                nodes = min(len(input_files), run.agent.max_nodes) if input_files is not None and not run.agent.job_array else 1
                gpu = run.agent.gpu and ('gpu' in workflow['config'] and workflow['config']['gpu'])

                if 'cores' in resources:
                    cores = int(resources['cores'])
                    script.write(f"#SBATCH --cpus-per-task={cores}\n")
                if 'time' in resources:
                    split_time = resources['time'].split(':')
                    hours = int(split_time[0])
                    minutes = int(split_time[1])
                    seconds = int(split_time[2])
                    time = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                    # calculated [requested walltime * input files / nodes]
                    if input_files is not None:
                        adjusted_time = time * (len(input_files) / nodes)
                    else:
                        adjusted_time = time
                    hours = f"{min(ceil(adjusted_time.total_seconds() / 60 / 60), run.agent.max_nodes)}"
                    if len(hours) == 1:
                        hours = f"0{hours}"
                    adjusted_time_str = f"{hours}:00:00"

                    run.job_requested_walltime = adjusted_time_str
                    run.save()
                    msg = f"Using adjusted walltime {adjusted_time_str}"
                    update_status(run, msg)
                    logger.info(msg)

                    script.write(f"#SBATCH --time={adjusted_time_str}\n")
                if 'mem' in resources and (run.agent.header_skip is None or '--mem' not in str(run.agent.header_skip)):
                    mem = resources['mem']
                    script.write(f"#SBATCH --mem={resources['mem']}\n")
                if run.agent.queue is not None and run.agent.queue != '':
                    queue = run.agent.gpu_queue if gpu else run.agent.queue
                    script.write(f"#SBATCH --partition={queue}\n")
                if run.agent.project is not None and run.agent.project != '':
                    script.write(f"#SBATCH -A {run.agent.project}\n")
                if gpu:
                    script.write(f"#SBATCH --gres=gpu:1\n")

                if input_files is not None and run.agent.job_array:
                    script.write(f"#SBATCH --array=1-{len(input_files)}\n")
                if input_files is not None:
                    script.write(f"#SBATCH -N {nodes}\n")
                    script.write(f"#SBATCH --ntasks={nodes}\n")
                else:
                    script.write(f"#SBATCH -N 1\n")
                    script.write("#SBATCH --ntasks=1\n")

                script.write("#SBATCH --mail-type=END,FAIL\n")
                script.write(f"#SBATCH --mail-user={run.user.email}\n")
                script.write("#SBATCH --output=plantit.%j.out\n")
                script.write("#SBATCH --error=plantit.%j.err\n")

            # add precommands
            script.write(run.agent.pre_commands + '\n')

            # pull singularity container in advance
            # script.write(f"singularity pull {run_options.image}\n")

            # if we have inputs, add pull command
            if 'input' in workflow['config']:
                input = workflow['config']['input']
                sftp.mkdir(join(run.agent.workdir, run.workdir, 'input'))

                # allow for both spellings of JPG
                patterns = [pattern.lower() for pattern in input['patterns']]
                if 'jpg' in patterns and 'jpeg' not in patterns:
                    patterns.append("jpeg")
                elif 'jpeg' in patterns and 'jpg' not in patterns:
                    patterns.append("jpg")

                pull_commands = f"plantit terrain pull \"{input['from']}\"" \
                                f" -p \"{join(run.agent.workdir, run.workdir, 'input')}\"" \
                                f" {' '.join(['--pattern ' + pattern for pattern in patterns])}" \
                                f""f" --terrain_token {run.user.profile.cyverse_token}"

                if run.agent.callbacks:
                    pull_commands += f""f" --plantit_url '{callback_url}' --plantit_token '{run.token}'"
                pull_commands += "\n"

                logger.info(f"Using pull command: {pull_commands}")
                script.write(pull_commands)

            docker_username = environ.get('DOCKER_USERNAME', None)
            docker_password = environ.get('DOCKER_PASSWORD', None)

            # if this resource uses TACC's launcher, create a parameter sweep script to invoke Singularity
            if launcher:
                logger.info(f"Using TACC launcher")
                with sftp.open('launch', 'w') as launcher_script:
                    if workflow['config']['input']['kind'] == 'files' and input_files is not None:
                        for file in input_files:
                            file_name = file.rpartition('/')[2]
                            run_options.input = FileInput(file_name)
                            command = prep_run_command(
                                work_dir=run_options.workdir,
                                image=run_options.image,
                                command=run_options.command,
                                parameters=(run_options.parameters if run_options.parameters is not None else []) + [
                                    Parameter(key='INPUT', value=join(run.agent.workdir, run.workdir, 'input', file_name))],
                                bind_mounts=run_options.bind_mounts,
                                docker_username=docker_username,
                                docker_password=docker_password,
                                no_cache=run_options.no_cache,
                                gpu=run_options.gpu)
                            launcher_script.write(f"{command}\n")
                    elif workflow['config']['input']['kind'] == 'directory':
                        command = prep_run_command(
                            work_dir=run_options.workdir,
                            image=run_options.image,
                            command=run_options.command,
                            parameters=(run_options.parameters if run_options.parameters is not None else []) + [
                                Parameter(key='INPUT', value=join(run.agent.workdir, run.workdir, 'input'))],
                            bind_mounts=run_options.bind_mounts,
                            docker_username=docker_username,
                            docker_password=docker_password,
                            no_cache=run_options.no_cache,
                            gpu=run_options.gpu)
                        launcher_script.write(f"{command}\n")
                    elif workflow['config']['input']['kind'] == 'file':
                        command = prep_run_command(
                            work_dir=run_options.workdir,
                            image=run_options.image,
                            command=run_options.command,
                            parameters=(run_options.parameters if run_options.parameters is not None else []) + [
                                Parameter(key='INPUT', value=new_flow['input']['file']['path'])],
                            bind_mounts=run_options.bind_mounts,
                            docker_username=docker_username,
                            docker_password=docker_password,
                            no_cache=run_options.no_cache,
                            gpu=run_options.gpu)
                        launcher_script.write(f"{command}\n")

                script.write(f"export LAUNCHER_WORKDIR={join(run.agent.workdir, run.workdir)}\n")
                script.write(f"export LAUNCHER_JOB_FILE=launch\n")
                script.write("$LAUNCHER_DIR/paramrun\n")
            # otherwise use the CLI
            else:
                run_commands = f"plantit run flow.yaml"
                if run.agent.job_array and input_files is not None:
                    run_commands += f" --slurm_job_array"

                if docker_username is not None and docker_password is not None:
                    run_commands += f" --docker_username {docker_username} --docker_password {docker_password}"

                if run.agent.callbacks:
                    run_commands += f""f" --plantit_url '{callback_url}' --plantit_token '{run.token}'"

                run_commands += "\n"
                logger.info(f"Using CLI run command: {run_commands}")
                script.write(run_commands)

            # add zip command
            output = workflow['config']['output']
            zip_commands = f"plantit zip {output['from'] if output['from'] != '' else '.'} -o . -n {run.guid}"
            log_files = [f"{run.guid}.{run.agent.name.lower()}.log"]
            zip_commands = f"{zip_commands} {' '.join(['--include_pattern ' + pattern for pattern in log_files])}"
            if 'include' in output:
                if 'patterns' in output['include']:
                    zip_commands = f"{zip_commands} {' '.join(['--include_pattern ' + pattern for pattern in output['include']['patterns']])}"
                if 'names' in output['include']:
                    zip_commands = f"{zip_commands} {' '.join(['--include_name ' + pattern for pattern in output['include']['names']])}"
                if 'patterns' in output['exclude']:
                    zip_commands = f"{zip_commands} {' '.join(['--exclude_pattern ' + pattern for pattern in output['exclude']['patterns']])}"
                if 'names' in output['exclude']:
                    zip_commands = f"{zip_commands} {' '.join(['--exclude_name ' + pattern for pattern in output['exclude']['names']])}"
            zip_commands += '\n'
            script.write(zip_commands)
            logger.info(f"Using zip command: {zip_commands}")

            # add push command if we have a destination
            # if 'to' in output and output['to'] is not None:
            #     push_commands = f"plantit terrain push {output['to']}" \
            #                     f" -p {join(run.work_dir, output['from'])}" \
            #                     f" --plantit_url '{callback_url}'"

            #     if 'include' in output:
            #         if 'patterns' in output['include']:
            #             push_commands = push_commands + ' '.join(
            #                 ['--include_pattern ' + pattern for pattern in output['include']['patterns']])
            #         if 'names' in output['include']:
            #             push_commands = push_commands + ' '.join(['--include_name ' + pattern for pattern in output['include']['names']])
            #         if 'patterns' in output['exclude']:
            #             push_commands = push_commands + ' '.join(
            #                 ['--exclude_pattern ' + pattern for pattern in output['exclude']['patterns']])
            #         if 'names' in output['exclude']:
            #             push_commands = push_commands + ' '.join(['--exclude_name ' + pattern for pattern in output['exclude']['names']])

            #     if run.resource.callbacks:
            #         push_commands += f""f" --plantit_url '{callback_url}' --plantit_token '{run.token}'"

            #     push_commands += '\n'
            #     script.write(push_commands)
            #     logger.info(f"Using push command: {push_commands}")