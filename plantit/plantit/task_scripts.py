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
from plantit.task_resources import push_task_channel_event, log_task_status

from plantit.tasks.models import Task, InputKind, TaskOptions, Parameter, EnvironmentVariable
from plantit.utils.agents import has_virtual_memory

from plantit.singularity import compose_singularity_invocation

logger = logging.getLogger(__name__)


# Values (command subcomponents) #

def calculate_node_count(task: Task, inputs: List[str]):
    node_count = min(len(inputs), task.agent.max_nodes)
    return 1 if task.agent.launcher else (node_count if inputs is not None and not task.agent.job_array else 1)


def calculate_walltime(task: Task, options: TaskOptions, inputs: List[str]):
    # TODO: refactor (https://github.com/Computational-Plant-Science/plantit/issues/205)

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


# Commands (script subcomponents) #

def compose_pull_headers(task: Task) -> List[str]:
    headers = []

    # memory
    if not has_virtual_memory(task.agent):
        headers.append(f"#SBATCH --mem=1GB")

    # walltime
    headers.append(f"#SBATCH --time=00:10:00")  # TODO: calculate as a function of input size?

    # queue
    queue = task.agent.orchestrator_queue if task.agent.orchestrator_queue is not None and task.agent.orchestrator_queue != '' else task.agent.queue
    headers.append(f"#SBATCH --partition={queue}")

    # project/allocation
    if task.agent.project is not None and task.agent.project != '':
        headers.append(f"#SBATCH -A {task.agent.project}")

    # nodes
    headers.append(f"#SBATCH -N 1")

    # cores
    headers.append(f"#SBATCH -n 1")

    # email notifications
    headers.append("#SBATCH --mail-type=END,FAIL")
    headers.append(f"#SBATCH --mail-user={task.user.email}")

    # log files
    headers.append("#SBATCH --output=plantit.%j.pull.out")
    headers.append("#SBATCH --error=plantit.%j.pull.err")

    return headers


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

    # singularity must be pre-authenticated on the agent, e.g. with `singularity remote login --username <your username> docker://docker.io`
    # also, if this is a job array, all jobs will invoke iget, but files will only be downloaded once (since we don't use -f for force)
    command = f"singularity exec {image} iget -r {input_path} {workdir}"

    logger.debug(f"Using pull command: {command}")
    return [command]


def compose_job_headers(task: Task, options: TaskOptions, inputs: List[str]) -> List[str]:
    if 'jobqueue' not in options: return []
    jobqueue = options['jobqueue']
    headers = []

    # memory
    if ('memory' in jobqueue or 'mem' in jobqueue) and not has_virtual_memory(task.agent):
        memory = jobqueue['memory'] if 'memory' in jobqueue else jobqueue['mem']
        headers.append(f"#SBATCH --mem={'1GB' if task.agent.orchestrator_queue is not None else memory}")

    # walltime
    if 'walltime' in jobqueue or 'time' in jobqueue:
        walltime = calculate_walltime(task, options, inputs)
        # task.job_requested_walltime = walltime
        # task.save()
        headers.append(f"#SBATCH --time={walltime}")

    # queue/partition
    if task.agent.orchestrator_queue is not None and task.agent.orchestrator_queue != '':
        headers.append(f"#SBATCH --partition={task.agent.orchestrator_queue}")
    else:
        headers.append(f"#SBATCH --partition={task.agent.queue}")

    # allocation
    if task.agent.project is not None and task.agent.project != '':
        headers.append(f"#SBATCH -A {task.agent.project}")

    # cores per node
    if 'cores' in jobqueue:
        headers.append(f"#SBATCH -n {int(jobqueue['cores'])}")

    # nodes & tasks per node
    nodes = calculate_node_count(task, inputs)
    tasks = min(len(inputs), task.agent.max_cores)
    if len(inputs) > 0 and options['input']['kind'] == 'files':
        if task.agent.job_array: headers.append(f"#SBATCH --array=1-{len(inputs)}")
        headers.append(f"#SBATCH -N {nodes}")
        headers.append(f"#SBATCH --ntasks={tasks if inputs is not None and not task.agent.job_array else 1}")
    else:
        headers.append(f"#SBATCH -N 1")
        headers.append("#SBATCH --ntasks=1")

    # gpus
    gpus = options['gpus'] if 'gpus' in options else 0
    if gpus and task.agent.orchestrator_queue is None:
        headers.append(f"#SBATCH --gres=gpu:{gpus}")

    # email notifications
    headers.append("#SBATCH --mail-type=END,FAIL")
    headers.append(f"#SBATCH --mail-user={task.user.email}")

    # log files
    headers.append("#SBATCH --output=plantit.%j.out")
    headers.append("#SBATCH --error=plantit.%j.err")

    newline = '\n'
    logger.debug(f"Using headers: {newline.join(headers)}")
    return headers


def compose_job_commands(task: Task, options: TaskOptions) -> List[str]:
    commands = []

    # if this agent uses TACC's launcher, invoke the parameter sweep script
    if task.agent.launcher:
        commands.append(f"export LAUNCHER_WORKDIR={join(task.agent.workdir, task.workdir)}")
        commands.append(f"export LAUNCHER_JOB_FILE={os.environ.get('LAUNCHER_SCRIPT_NAME')}")
        commands.append("$LAUNCHER_DIR/paramrun")
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

        if 'input' in options:
            kind = options['input']['kind']
            if kind == 'files' or kind == 'file':
                input_path_name = options['input']['path'].rpartition('/')[2]
                full_input_path = join(options['workdir'], 'input', input_path_name, '$file') if kind == 'files' else join(options['workdir'], 'input', '$file')
                commands.append(f"file=$(head -n $SLURM_ARRAY_TASK_ID {settings.INPUTS_FILE_NAME} | tail -1)")
                commands = commands + compose_singularity_invocation(
                    work_dir=work_dir,
                    image=image,
                    commands=command,
                    env=env,
                    parameters=parameters + [Parameter(key='INPUT', value=full_input_path), Parameter(key='INDEX', value='$SLURM_ARRAY_TASK_ID')],
                    bind_mounts=bind_mounts,
                    no_cache=no_cache,
                    gpus=gpus,
                    shell=shell)
            elif options['input']['kind'] == 'directory':
                input_path_name = options['input']['path'].rpartition('/')[2]
                commands = commands + compose_singularity_invocation(
                    work_dir=work_dir,
                    image=image,
                    commands=command,
                    env=env,
                    parameters=parameters + [Parameter(key='INPUT', value=join(options['workdir'], 'input', input_path_name))],
                    bind_mounts=bind_mounts,
                    no_cache=no_cache,
                    gpus=gpus,
                    shell=shell)
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
                shell=shell)

    newline = '\n'
    logger.debug(f"Using container commands: {newline.join(commands)}")
    return commands


def compose_push_headers(task: Task) -> List[str]:
    headers = []

    # memory
    if not has_virtual_memory(task.agent):
        headers.append(f"#SBATCH --mem=1GB")

    # walltime
    headers.append(f"#SBATCH --time=00:10:00")  # TODO: calculate as a function of input size?

    # queue
    queue = task.agent.orchestrator_queue if task.agent.orchestrator_queue is not None and task.agent.orchestrator_queue != '' else task.agent.queue
    headers.append(f"#SBATCH --partition={queue}")

    # project/allocation
    if task.agent.project is not None and task.agent.project != '':
        headers.append(f"#SBATCH -A {task.agent.project}")

    # nodes
    headers.append(f"#SBATCH -N 1")

    # cores
    headers.append(f"#SBATCH -n 1")

    # email notifications
    headers.append("#SBATCH --mail-type=END,FAIL")
    headers.append(f"#SBATCH --mail-user={task.user.email}")

    # log files
    headers.append("#SBATCH --output=plantit.%j.push.out")
    headers.append("#SBATCH --error=plantit.%j.push.err")

    return headers


def compose_push_commands(task: Task, options: TaskOptions) -> List[str]:
    commands = []

    # create staging directory
    staging_dir = f"{task.guid}_staging"
    mkdir_command = f"mkdir -p {staging_dir}"
    commands.append(mkdir_command)

    # move results into staging directory
    mv_command = f"mv -t {staging_dir} "
    output = options['output']
    if 'include' in output:
        if 'names' in output['include']:
            for name in output['include']['names']:
                mv_command = mv_command + f"{name} "
        if 'patterns' in output['include']:
            for pattern in (list(output['include']['patterns']) + ['out', 'err', 'zip']):
                mv_command = mv_command + f"*.{pattern} "
    else: raise ValueError(f"No output filenames & patterns to include")
    commands.append(mv_command)

    # filter unwanted results from staging directory
    # TODO: can we do this in a single step with mv?
    # rm_command = f"rm "
    # if 'exclude' in output:
    #     if 'patterns' in output['exclude']:
    #         command = command + ' ' + ' '.join(
    #             ['--exclude_pattern ' + pattern for pattern in output['exclude']['patterns']])
    #     if 'names' in output['exclude']:
    #         command = command + ' ' + ' '.join(
    #             ['--exclude_name ' + pattern for pattern in output['exclude']['names']])

    # zip results
    zip_command = f"zip -r {join(staging_dir, task.guid + '.zip')} {staging_dir}/*"
    commands.append(zip_command)

    path = output['to']
    image = f"docker://{settings.ICOMMANDS_IMAGE}"
    push_command = f"singularity exec {image} iput -f {staging_dir}/* {path}"
    commands.append(push_command)

    newline = '\n'
    logger.debug(f"Using push commands: {newline.join(commands)}")
    return commands


# Job Scripts #

def compose_pull_script(task: Task, options: TaskOptions) -> List[str]:
    with open(settings.TASKS_TEMPLATE_SCRIPT_SLURM, 'r') as template_file:
        template = [line.strip() for line in template_file if line != '']
        headers = compose_pull_headers(task)
        pull = compose_pull_commands(task, options)
        return template + \
               headers + \
               [task.agent.pre_commands] + \
               pull


def compose_job_script(task: Task, options: TaskOptions, inputs: List[str]) -> List[str]:
    with open(settings.TASKS_TEMPLATE_SCRIPT_SLURM, 'r') as template_file:
        template = [line.strip() for line in template_file if line != '']
        headers = compose_job_headers(task, options, inputs)
        run = compose_job_commands(task, options)
        return template + \
               headers + \
               [task.agent.pre_commands] + \
               run


def compose_push_script(task: Task, options: TaskOptions) -> List[str]:
    with open(settings.TASKS_TEMPLATE_SCRIPT_SLURM, 'r') as template_file:
        template = [line.strip() for line in template_file if line != '']
        headers = compose_push_headers(task)
        push = compose_push_commands(task, options)
        return template + \
               headers + \
               [task.agent.pre_commands] + \
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
                shell=shell)
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
                shell=shell)
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
            shell=shell)

    return lines
