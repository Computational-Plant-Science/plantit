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
from plantit.task_resources import push_task_channel_event, log_task_orchestrator_status

from plantit.tasks.models import Task, InputKind, TaskOptions, Parameter, EnvironmentVariable
from plantit.utils.agents import has_virtual_memory

from plantit.singularity import compose_singularity_invocation

logger = logging.getLogger(__name__)


# commands

def compose_headers(task: Task, options: TaskOptions, inputs: List[str]) -> List[str]:
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
        task.job_requested_walltime = walltime
        task.save()
        commands.append(f"#SBATCH --time={walltime}")
    if gpus and task.agent.orchestrator_queue is None: commands.append(f"#SBATCH --gres=gpu:{gpus}")
    if task.agent.orchestrator_queue is not None and task.agent.orchestrator_queue != '':
        commands.append(f"#SBATCH --partition={task.agent.orchestrator_queue}")
    elif task.agent.queue is not None and task.agent.queue != '':
        commands.append(f"#SBATCH --partition={task.agent.queue}")
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
    logger.debug(f"Using headers: {newline.join(commands)}")
    return commands


def compose_pull_commands(task: Task, options: TaskOptions) -> List[str]:
    if 'input' not in options: return []
    input = options['input']
    if input is None: return []
    # kind = input['kind']
    # patterns = []
    # if kind != InputKind.FILE and 'patterns' in input:
    #     # allow for both spellings of JPG
    #     patterns = [pattern.lower() for pattern in input['patterns']]
    #     if 'jpg' in patterns and 'jpeg' not in patterns:
    #         patterns.append("jpeg")
    #     elif 'jpeg' in patterns and 'jpg' not in patterns:
    #         patterns.append("jpg")

    # command = f"plantit terrain pull \"{input['path']}\"" \
    #           f" -p \"{join(task.agent.workdir, task.workdir, 'input')}\"" \
    #           f" {' '.join(['--pattern ' + pattern for pattern in patterns])}" \
    #           f""f" --terrain_token {task.user.profile.cyverse_access_token}"
    input_path = input['path']
    workdir = join(task.agent.workdir, task.workdir, 'input')
    image = f"docker://{settings.ICOMMANDS_IMAGE}"
    # command = f"SINGULARITY_DOCKER_USERNAME={settings.DOCKER_USERNAME} SINGULARITY_DOCKER_PASSWORD={settings.DOCKER_PASSWORD} " \
    #           f"singularity exec --home {workdir} {image} iget {input_path} {workdir}"
              # f"bash -c \"echo '{settings.CYVERSE_PASSWORD}' | iget {input_path} {workdir}\""
    command = f"singularity exec {image} iget {input_path} {workdir}"

    logger.debug(f"Using pull command: {command}")
    return [command]


def compose_container_commands(task: Task, options: TaskOptions) -> List[str]:
    commands = []

    # if this agent uses TACC's launcher, invoke the parameter sweep script
    if task.agent.launcher:
        commands.append(f"export LAUNCHER_WORKDIR={join(task.agent.workdir, task.workdir)}\n")
        commands.append(f"export LAUNCHER_JOB_FILE={os.environ.get('LAUNCHER_SCRIPT_NAME')}\n")
        commands.append("$LAUNCHER_DIR/paramrun\n")
    # otherwise use SLURM job arrays
    else:
        work_dir = options['workdir']
        image = options['image']
        command = options['command']
        env = options['env']
        gpus = options[
            'gpus'] if 'gpus' in options else 0  # TODO: if workflow is configured for gpu, use the number of gpus configured on the agent
        parameters = (options['parameters'] if 'parameters' in options else []) + [
            Parameter(key='OUTPUT', value=options['output']['from']),
            Parameter(key='GPUS', value=str(gpus))]
        bind_mounts = options['bind_mounts'] if (
                'bind_mounts' in options and isinstance(options['bind_mounts'], list)) else []
        no_cache = options['no_cache'] if 'no_cache' in options else False
        shell = options['shell'] if 'shell' in options else None
        docker_username = environ.get('DOCKER_USERNAME', None)
        docker_password = environ.get('DOCKER_PASSWORD', None)

        if 'input' in options:
            if options['input']['kind'] == 'files' or options['input']['kind'] == 'file':
                commands.append(f"file=$(head -n $SLURM_ARRAY_TASK_ID test.txt | tail -1)")
                commands = commands + compose_singularity_invocation(
                    work_dir=work_dir,
                    image=image,
                    commands=command,
                    env=env,
                    parameters=parameters + [Parameter(key='INPUT', value=join(options['workdir'], 'input', '$file'))],
                    bind_mounts=bind_mounts,
                    no_cache=no_cache,
                    gpus=gpus,
                    shell=shell,
                    docker_username=docker_username,
                    docker_password=docker_password)
            elif options['input']['kind'] == 'directory':
                commands = commands + compose_singularity_invocation(
                    work_dir=work_dir,
                    image=image,
                    commands=command,
                    env=env,
                    parameters=parameters + [Parameter(key='INPUT', value=join(options['workdir'], 'input'))],
                    bind_mounts=bind_mounts,
                    no_cache=no_cache,
                    gpus=gpus,
                    shell=shell,
                    docker_username=docker_username,
                    docker_password=docker_password)
        else:
            commands = commands + compose_singularity_invocation(
                work_dir=work_dir,
                image=image,
                commands=command,
                env=env,
                parameters=parameters,
                bind_mounts=options['bind_mounts'] if 'bind_mounts' in options else None,
                no_cache=no_cache,
                gpus=gpus,
                shell=shell,
                docker_username=docker_username,
                docker_password=docker_password)

    newline = '\n'
    logger.debug(f"Using container commands: {newline.join(commands)}")
    return commands


def compose_zip_commands(task: Task, options: TaskOptions) -> List[str]:
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

    # TODO: refactor to use `zip`
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
    return [command]


def compose_push_commands(task: Task, options: TaskOptions) -> List[str]:
    commands = []
    if 'output' not in options: return commands
    output = options['output']
    if output is None: return commands

    # add push command if we have a destination
    if 'to' not in output or output['to'] is None:
        return commands

    staging_dir = f"{task.guid}_staging"
    commands.append(f"mkdir -p {staging_dir}")
    mv_command = f"mv -t {staging_dir}"

    if 'include' in output:
        if 'names' in output['include']:
            mv_command = mv_command + ' ' + ' '.join([pattern for pattern in output['include']['names']])
        if 'patterns' in output['include']:
            patterns = list(output['include']['patterns'])
            patterns.append('out')
            patterns.append('err')
            patterns.append('zip')
            mv_command = mv_command + ' ' + ' '.join([f"*.{pattern}" for pattern in patterns])
    else:
        raise ValueError(f"Expected names & patterns to include")

    commands.append(mv_command)

    # if 'exclude' in output:
    #     if 'patterns' in output['exclude']:
    #         command = command + ' ' + ' '.join(
    #             ['--exclude_pattern ' + pattern for pattern in output['exclude']['patterns']])
    #     if 'names' in output['exclude']:
    #         command = command + ' ' + ' '.join(
    #             ['--exclude_name ' + pattern for pattern in output['exclude']['names']])

    # command += f" --terrain_token '{task.user.profile.cyverse_access_token}'"

    to_path = output['to']
    from_path = join(task.agent.workdir, task.workdir, output['from'])
    image = f"docker://{settings.ICOMMANDS_IMAGE}"
    # push_command = f"SINGULARITY_DOCKER_USERNAME={settings.DOCKER_USERNAME} SINGULARITY_DOCKER_PASSWORD={settings.DOCKER_PASSWORD} " \
    #                f"singularity exec --home {from_path} {image} iput {from_path} {to_path}"
                   # f"bash -c \"echo '{settings.CYVERSE_PASSWORD}' | iput {from_path} {to_path}\""
    push_command = f"singularity exec {image} iput -f {staging_dir}/* {to_path}"

    commands.append(push_command)

    newline = '\n'
    logger.debug(f"Using push commands: {newline.join(commands)}")
    return commands


# scripts

def compose_job_script(task: Task, options: TaskOptions, inputs: List[str]) -> List[str]:
    with open(settings.TASKS_TEMPLATE_SCRIPT_SLURM, 'r') as template_file:
        template = [line.strip() for line in template_file if line != '']
        headers = compose_headers(task, options, inputs)
        pull = compose_pull_commands(task, options)
        run = compose_container_commands(task, options)
        # zip = compose_zip_commands(task, options)
        push = compose_push_commands(task, options)

        return template + \
               headers + \
               [task.agent.pre_commands] + \
               pull + \
               run + \
               push


def compose_launcher_script(task: Task, options: TaskOptions, inputs: List[str]) -> List[str]:
    lines: List[str] = []
    work_dir = options['workdir']
    image = options['image']
    command = options['command']
    env = options['env']
    gpus = options[
        'gpus'] if 'gpus' in options else 0  # TODO: if workflow is configured for gpu, use the number of gpus configured on the agent
    parameters = (options['parameters'] if 'parameters' in options else []) + [
        Parameter(key='OUTPUT', value=options['output']['from']),
        Parameter(key='GPUS', value=str(gpus))]
    bind_mounts = options['bind_mounts'] if (
            'bind_mounts' in options and isinstance(options['bind_mounts'], list)) else []
    no_cache = options['no_cache'] if 'no_cache' in options else False
    shell = options['shell'] if 'shell' in options else None
    docker_username = environ.get('DOCKER_USERNAME', None)
    docker_password = environ.get('DOCKER_PASSWORD', None)

    if 'input' in options:
        if options['input']['kind'] == 'files':
            for i, file in enumerate(inputs):
                lines = lines + compose_singularity_invocation(
                    work_dir=work_dir,
                    image=image,
                    commands=command,
                    env=env,
                    parameters=parameters + [Parameter(key='INPUT', value=join(options['workdir'], 'input', file))],
                    bind_mounts=bind_mounts,
                    no_cache=no_cache,
                    gpus=gpus,
                    shell=shell,
                    docker_username=docker_username,
                    docker_password=docker_password,
                    index=i)
        elif options['input']['kind'] == 'directory':
            lines = lines + compose_singularity_invocation(
                work_dir=work_dir,
                image=image,
                commands=command,
                env=env,
                parameters=parameters + [Parameter(key='INPUT', value=join(options['workdir'], 'input'))],
                bind_mounts=bind_mounts,
                no_cache=no_cache,
                gpus=gpus,
                shell=shell,
                docker_username=docker_username,
                docker_password=docker_password)
        elif options['input']['kind'] == 'file':
            lines = lines + compose_singularity_invocation(
                work_dir=work_dir,
                image=image,
                commands=command,
                env=env,
                parameters=parameters + [Parameter(key='INPUT', value=join(options['workdir'], 'input', inputs[0]))],
                bind_mounts=bind_mounts,
                no_cache=no_cache,
                gpus=gpus,
                shell=shell,
                docker_username=docker_username,
                docker_password=docker_password)
    else:
        lines = lines + compose_singularity_invocation(
            work_dir=work_dir,
            image=image,
            commands=command,
            env=env,
            parameters=parameters,
            bind_mounts=options['bind_mounts'] if 'bind_mounts' in options else None,
            no_cache=no_cache,
            gpus=gpus,
            shell=shell,
            docker_username=docker_username,
            docker_password=docker_password)

    return lines


# utils

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
        if units.lower() == 'hours':
            walltime = timedelta(hours=limit, minutes=0, seconds=0)
        elif units.lower() == 'minutes':
            walltime = timedelta(hours=0, minutes=limit, seconds=0)
        elif units.lower() == 'seconds':
            walltime = timedelta(hours=0, minutes=0, seconds=limit)

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
    hours = min(job_walltime, agent_walltime)
    hours = '1' if hours == 0 else f"{hours}"
    if len(hours) == 1: hours = f"0{hours}"
    adjusted_str = f"{hours}:00:00"

    logger.info(f"Using walltime {adjusted_str} for {task.user.username}'s task {task.guid}")
    return adjusted_str
