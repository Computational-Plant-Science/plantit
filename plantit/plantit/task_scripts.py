import os
import logging
from datetime import timedelta

from asgiref.sync import async_to_sync
from math import ceil
from os import environ
from os.path import join
from typing import List

from django.conf import settings

from plantit import terrain as terrain
from plantit.agents.models import AgentScheduler
from plantit.task_resources import push_task_channel_event, log_task_orchestrator_status

from plantit.tasks.models import Task, InputKind, TaskOptions, EnvironmentVariable, BindMount, Parameter
from plantit.utils.agents import has_virtual_memory
from plantit.utils.tasks import format_bind_mount

logger = logging.getLogger(__name__)


def compose_task_pull_command(task: Task, options: TaskOptions) -> str:
    if 'input' not in options: return ''
    input = options['input']
    if input is None: return ''
    kind = input['kind']

    if kind != InputKind.FILE and 'patterns' in input:
        # allow for both spellings of JPG
        patterns = [pattern.lower() for pattern in input['patterns']]
        if 'jpg' in patterns and 'jpeg' not in patterns: patterns.append("jpeg")
        elif 'jpeg' in patterns and 'jpg' not in patterns: patterns.append("jpg")
    else:
        patterns = []

    command = f"plantit terrain pull \"{input['path']}\"" \
              f" -p \"{join(task.agent.workdir, task.workdir, 'input')}\"" \
              f" {' '.join(['--pattern ' + pattern for pattern in patterns])}" \
              f""f" --terrain_token {task.user.profile.cyverse_access_token}"

    logger.debug(f"Using pull command: {command}")
    return command


def compose_task_run_commands(task: Task, options: TaskOptions, inputs: List[str]) -> List[str]:
    docker_username = environ.get('DOCKER_USERNAME', None)
    docker_password = environ.get('DOCKER_PASSWORD', None)
    commands = []

    # if this resource uses TACC's launcher, create a parameter sweep script to invoke the Singularity container
    if task.agent.launcher:
        commands.append(f"export LAUNCHER_WORKDIR={join(task.agent.workdir, task.workdir)}\n")
        commands.append(f"export LAUNCHER_JOB_FILE={os.environ.get('LAUNCHER_SCRIPT_NAME')}\n")
        commands.append("$LAUNCHER_DIR/paramrun\n")
    # otherwise use the CLI
    else:
        command = f"plantit run {task.guid}.yaml"
        if task.agent.job_array and len(inputs) > 0:
            command += f" --slurm_job_array"

        if docker_username is not None and docker_password is not None:
            command += f" --docker_username {docker_username} --docker_password {docker_password}"

        commands.append(command)

    newline = '\n'
    logger.debug(f"Using CLI commands: {newline.join(commands)}")
    return commands


def compose_task_clean_commands(task: Task) -> str:
    docker_username = environ.get('DOCKER_USERNAME', None)
    docker_password = environ.get('DOCKER_PASSWORD', None)
    cmd = f"plantit clean *.out -p {docker_username} -p {docker_password}"
    cmd += f"\nplantit clean *.err -p {docker_username} -p {docker_password}"

    if task.agent.launcher:
        workdir = join(task.agent.workdir, task.workdir)
        launcher_script = join(workdir, os.environ.get('LAUNCHER_SCRIPT_NAME'))
        cmd += f"\nplantit clean {launcher_script} -p {docker_username} -p {docker_password} "

    return cmd


def compose_task_zip_command(task: Task, options: TaskOptions) -> str:
    if 'output' in options:
        output = options['output']
    else:
        output = dict()
        output['include'] = dict()
        output['include']['names'] = dict()
        output['include']['patterns'] = dict()
        output['exclude'] = dict()
        output['exclude']['names'] = dict()
        output['exclude']['patterns'] = dict()

    # merge output patterns and files from workflow config
    config = task.workflow
    if 'output' in config:
        if 'include' in config['output']:
            if 'patterns' in config['output']['include']:
                output['include']['patterns'] = list(
                    set(output['include']['patterns'] + config['output']['include']['patterns']))
            if 'names' in config['output']['include']:
                output['include']['names'] = list(
                    set(output['include']['names'] + config['output']['include']['names']))
        if 'exclude' in config['output']:
            if 'patterns' in config['output']['exclude']:
                output['exclude']['patterns'] = list(
                    set(output['exclude']['patterns'] + config['output']['exclude']['patterns']))
            if 'names' in config['output']['exclude']:
                output['exclude']['names'] = list(
                    set(output['exclude']['names'] + config['output']['exclude']['names']))

    command = f"plantit zip {output['from'] if 'from' in output and output['from'] != '' else '.'} -o . -n {task.guid}"
    logs = [f"{task.guid}.{task.agent.name.lower()}.log"]
    command = f"{command} {' '.join(['--include_pattern ' + pattern for pattern in logs])}"

    if 'include' in output:
        if 'patterns' in output['include']:
            command = f"{command} {' '.join(['--include_pattern ' + pattern for pattern in output['include']['patterns']])}"
        if 'names' in output['include']:
            command = f"{command} {' '.join(['--include_name ' + pattern for pattern in output['include']['names']])}"
    if 'exclude' in output:
        if 'patterns' in output['exclude']:
            command = f"{command} {' '.join(['--exclude_pattern ' + pattern for pattern in output['exclude']['patterns']])}"
        if 'names' in output['exclude']:
            command = f"{command} {' '.join(['--exclude_name ' + pattern for pattern in output['exclude']['names']])}"

    logger.debug(f"Using zip command: {command}")
    return command


def compose_task_push_command(task: Task, options: TaskOptions) -> str:
    command = ''
    if 'output' not in options: return command
    output = options['output']
    if output is None: return command

    # add push command if we have a destination
    if 'to' in output and output['to'] is not None:
        command = f"plantit terrain push {output['to']} -p {join(task.agent.workdir, task.workdir, output['from'])} "

        if 'include' in output:
            if 'patterns' in output['include']:
                patterns = list(output['include']['patterns'])
                patterns.append('.out')
                patterns.append('.err')
                patterns.append('.zip')
                command = command + ' ' + ' '.join(['--include_pattern ' + pattern for pattern in patterns])
            if 'names' in output['include']:
                command = command + ' ' + ' '.join(
                    ['--include_name ' + pattern for pattern in output['include']['names']])
        if 'exclude' in output:
            if 'patterns' in output['exclude']:
                command = command + ' ' + ' '.join(
                    ['--exclude_pattern ' + pattern for pattern in output['exclude']['patterns']])
            if 'names' in output['exclude']:
                command = command + ' ' + ' '.join(
                    ['--exclude_name ' + pattern for pattern in output['exclude']['names']])

        command += f" --terrain_token '{task.user.profile.cyverse_access_token}'"

    logger.debug(f"Using push command: {command}")
    return command


def compose_task_run_script(task: Task, options: TaskOptions, template: str) -> List[str]:
    with open(template, 'r') as template_file:
        template_header = [line.strip() for line in template_file if line != '']

    if 'input' in options and options['input'] is not None:
        kind = options['input']['kind']
        path = options['input']['path']
        cyverse_token = task.user.profile.cyverse_access_token
        inputs = [terrain.get_file(path, cyverse_token)] if kind == InputKind.FILE else terrain.list_dir(path,
                                                                                                         cyverse_token)
    else:
        inputs = []

    resource_requests = compose_task_resource_requests(task, options, inputs)
    cli_pull = compose_task_pull_command(task, options)
    cli_run = compose_task_run_commands(task, options, inputs)
    cli_clean = compose_task_clean_commands(task)
    cli_zip = compose_task_zip_command(task, options)
    cli_push = compose_task_push_command(task, options)

    return template_header + \
           resource_requests + \
           [task.agent.pre_commands] + \
           [cli_pull] + \
           cli_run + \
           [cli_clean] + \
           [cli_zip] + \
           [cli_push]


def compose_task_singularity_command(
        work_dir: str,
        image: str,
        command: str,
        env: List[EnvironmentVariable] = None,
        bind_mounts: List[BindMount] = None,
        parameters: List[Parameter] = None,
        no_cache: bool = False,
        gpus: int = 0,
        docker_username: str = None,
        docker_password: str = None,
        index: int = None) -> str:
    # build up the command according to the order:
    # - (non-secret) env vars
    # - singularity invocation
    # - bind mounts
    # - cache & gpu options
    #
    # then prepend
    # - parameters
    # - secret env vars

    cmd = ''
    if env is not None:
        if len(env) > 0: cmd += ' '.join([f"SINGULARITYENV_{v['key'].upper().replace(' ', '_')}=\"{v['value']}\"" for v in env])
        cmd += ' '
    if parameters is None: parameters = []
    if index is not None: parameters.append(Parameter(key='INDEX', value=str(index)))
    parameters.append(Parameter(key='WORKDIR', value=work_dir))
    for parameter in parameters:
        key = parameter['key'].upper().replace(' ', '_')
        val = str(parameter['value'])
        cmd += f" SINGULARITYENV_{key}=\"{val}\""
    cmd += f" singularity exec --home {work_dir}"
    if bind_mounts is not None and len(bind_mounts) > 0:
        cmd += (' --bind ' + ','.join([format_bind_mount(work_dir, mount_point) for mount_point in bind_mounts]))
    if no_cache: cmd += ' --disable-cache'
    if gpus: cmd += ' --nv'
    cmd += f" {image} sh -c '{command}'"  # is `sh -c '[the command to run]'` always available/safe?
    logger.debug(f"Using command: '{cmd}'")  # don't want to reveal secrets so log before prepending secret env vars
    if docker_username is not None and docker_password is not None:
        cmd = f"SINGULARITY_DOCKER_USERNAME={docker_username} SINGULARITY_DOCKER_PASSWORD={docker_password} " + cmd

    return cmd


def compose_task_resource_requests(task: Task, options: TaskOptions, inputs: List[str]) -> List[str]:
    nodes = calculate_node_count(task, inputs)
    tasks = min(len(inputs), task.agent.max_cores)
    task.inputs_detected = len(inputs)
    task.save()

    if 'jobqueue' not in options: return []
    gpus = options['gpus'] if 'gpus' in options else 0
    jobqueue = options['jobqueue']
    commands = []

    if 'cores' in jobqueue: commands.append(f"#SBATCH --cpus-per-task={int(jobqueue['cores'])}")
    if ('memory' in jobqueue or 'mem' in jobqueue) and not has_virtual_memory(task.agent):
        memory = jobqueue['memory'] if 'memory' in jobqueue else jobqueue['mem']
        commands.append(f"#SBATCH --mem={'1GB' if task.agent.orchestrator_queue is not None else memory}")
    if 'walltime' in jobqueue or 'time' in jobqueue:
        walltime = calculate_walltime(task, options, inputs)
        async_to_sync(push_task_channel_event)(task)
        task.job_requested_walltime = walltime
        task.save()
        commands.append(f"#SBATCH --time={walltime}")
    if gpus and task.agent.orchestrator_queue is None: commands.append(f"#SBATCH --gres=gpu:{gpus}")
    if task.agent.orchestrator_queue is not None and task.agent.orchestrator_queue != '': commands.append(f"#SBATCH --partition={task.agent.orchestrator_queue}")
    elif task.agent.queue is not None and task.agent.queue != '': commands.append(f"#SBATCH --partition={task.agent.queue}")
    if task.agent.project is not None and task.agent.project != '': commands.append(f"#SBATCH -A {task.agent.project}")
    if len(inputs) > 0 and options['input']['kind'] == 'files':
        if task.agent.job_array: commands.append(f"#SBATCH --array=1-{len(inputs)}")
        commands.append(f"#SBATCH -N {nodes}")
        commands.append(f"#SBATCH --ntasks={tasks if inputs is not None and not task.agent.job_array else 1}")
    else:
        commands.append(f"#SBATCH -N 1")
        commands.append("#SBATCH --ntasks=1")
    commands.append("#SBATCH --mail-type=END,FAIL")
    commands.append(f"#SBATCH --mail-user={task.user.email}")
    commands.append("#SBATCH --output=plantit.%j.out")
    commands.append("#SBATCH --error=plantit.%j.err")

    newline = '\n'
    logger.debug(f"Using resource requests: {newline.join(commands)}")
    return commands


def compose_task_launcher_script(task: Task, options: TaskOptions) -> List[str]:
    lines = []
    docker_username = environ.get('DOCKER_USERNAME', None)
    docker_password = environ.get('DOCKER_PASSWORD', None)
    # TODO: if workflow is configured for gpu, use the number of gpus configured on the agent
    gpus = options['gpus'] if 'gpus' in options else 0

    if 'input' in options:
        files = list_input_files(task, options) if (
                'input' in options and options['input']['kind'] == 'files') else []
        task.inputs_detected = len(files)
        task.save()

        if options['input']['kind'] == 'files':
            for i, file in enumerate(files):
                file_name = file.rpartition('/')[2]
                command = compose_task_singularity_command(
                    work_dir=options['workdir'],
                    image=options['image'],
                    command=options['command'],
                    env=options['env'],
                    parameters=(options['parameters'] if 'parameters' in options else []) + [
                        Parameter(key='INPUT', value=join(options['workdir'], 'input', file_name)),
                        Parameter(key='OUTPUT', value=options['output']['from']),
                        Parameter(key='GPUS', value=str(gpus))],
                    bind_mounts=options['bind_mounts'] if (
                            'bind_mounts' in options and isinstance(options['bind_mounts'], list)) else [],
                    no_cache=options['no_cache'] if 'no_cache' in options else False,
                    gpus=gpus,
                    docker_username=docker_username,
                    docker_password=docker_password,
                    index=i)
                lines.append(command)
        elif options['input']['kind'] == 'directory':
            command = compose_task_singularity_command(
                work_dir=options['workdir'],
                image=options['image'],
                command=options['command'],
                env=options['env'],
                parameters=(options['parameters'] if 'parameters' in options else []) + [
                    Parameter(key='INPUT', value=join(options['workdir'], 'input')),
                    Parameter(key='OUTPUT', value=options['output']['from']),
                    Parameter(key='GPUS', value=str(gpus))],
                bind_mounts=options['bind_mounts'] if 'bind_mounts' in options and isinstance(options['bind_mounts'],
                                                                                              list) else [],
                no_cache=options['no_cache'] if 'no_cache' in options else False,
                gpus=gpus,
                docker_username=docker_username,
                docker_password=docker_password)
            lines.append(command)
        elif options['input']['kind'] == 'file':
            file_name = options['input']['path'].rpartition('/')[2]
            command = compose_task_singularity_command(
                work_dir=options['workdir'],
                image=options['image'],
                command=options['command'],
                env=options['env'],
                parameters=(options['parameters'] if 'parameters' in options else []) + [
                    Parameter(key='INPUT', value=join(options['workdir'], 'input', file_name)),
                    Parameter(key='OUTPUT', value=options['output']['from']),
                    Parameter(key='GPUS', value=str(gpus))],
                bind_mounts=options['bind_mounts'] if 'bind_mounts' in options and isinstance(options['bind_mounts'],
                                                                                              list) else [],
                no_cache=options['no_cache'] if 'no_cache' in options else False,
                gpus=gpus,
                docker_username=docker_username,
                docker_password=docker_password)
            lines.append(command)
    else:
        command = compose_task_singularity_command(
            work_dir=options['workdir'],
            image=options['image'],
            command=options['command'],
            env=options['env'],
            parameters=options['parameters'] if 'parameters' in options else [] + [
                Parameter(key='OUTPUT', value=options['output']['from']),
                Parameter(key='GPUS', value=str(gpus))],
            bind_mounts=options['bind_mounts'] if 'bind_mounts' in options else None,
            no_cache=options['no_cache'] if 'no_cache' in options else False,
            gpus=gpus,
            docker_username=docker_username,
            docker_password=docker_password)
        lines.append(command)

    return lines


# utils

def list_input_files(task: Task, options: TaskOptions) -> List[str]:
    input_files = terrain.list_dir(options['input']['path'], task.user.profile.cyverse_access_token)
    msg = f"Found {len(input_files)} input file(s)"
    log_task_orchestrator_status(task, [msg])
    async_to_sync(push_task_channel_event)(task)
    logger.info(msg)

    return input_files


def calculate_node_count(task: Task, inputs: List[str]):
    node_count = min(len(inputs), task.agent.max_nodes)
    return 1 if task.agent.launcher else (node_count if inputs is not None and not task.agent.job_array else 1)


def calculate_walltime(task: Task, options: TaskOptions, inputs: List[str]):
    # by default, use the suggested walltime provided in plantit.yaml
    jobqueue = options['jobqueue']
    walltime = jobqueue['walltime' if 'walltime' in jobqueue else 'time']
    split_time = walltime.split(':')
    hours = int(split_time[0])
    minutes = int(split_time[1])
    seconds = int(split_time[2])
    walltime = timedelta(hours=hours, minutes=minutes, seconds=seconds)

    # if we have a manual (or preset) override, use that instead
    if 'time' in task.workflow and 'limit' in task.workflow['time'] and 'units' in task.workflow['time']:
        units = task.workflow['time']['units']
        limit = int(task.workflow['time']['limit'])
        if units.lower() == 'hours': walltime = timedelta(hours=limit, minutes=0, seconds=0)
        elif units.lower() == 'minutes': walltime = timedelta(hours=0, minutes=limit, seconds=0)
        elif units.lower() == 'seconds': walltime = timedelta(hours=0, minutes=0, seconds=limit)

    # TODO adjust to compensate for number of input files and parallelism [requested walltime * input files / nodes]
    # need to compute suggested walltime as a function of workflow, agent, and number of inputs
    # how to do this? cache suggestions for each combination independently?
    # issue ref: https://github.com/Computational-Plant-Science/plantit/issues/205
    #
    # a good first step might be to compute aggregate stats for runtimes per workflow per agent,
    # to get a sense for the scaling of each as a function of inputs and resources available
    #
    # naive (bad) solution:
    #   nodes = calculate_node_count(task, inputs)
    #   adjusted = walltime * (len(inputs) / nodes) if len(inputs) > 0 else walltime

    # round up to the nearest hour
    job_walltime = ceil(walltime.total_seconds() / 60 / 60)
    agent_walltime = int(int(task.agent.max_walltime) / 60)
    hours = f"{min(job_walltime, agent_walltime)}"
    if len(hours) == 1: hours = f"0{hours}"
    adjusted_str = f"{hours}:00:00"

    logger.info(f"Using walltime {adjusted_str} for {task.user.username}'s task {task.guid}")
    return adjusted_str
