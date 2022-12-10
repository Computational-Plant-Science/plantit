import os
import logging
from datetime import timedelta

from asgiref.sync import async_to_sync
from math import ceil
from os import environ
from os.path import join
from typing import List

from django.conf import settings

from plantit.task_resources import push_task_channel_event, log_task_status
from plantit.tasks.models import Task, InputKind, TaskOptions, Parameter, EnvironmentVariable
from plantit.utils.agents import has_virtual_memory
from plantit.singularity import compose_singularity_invocation

logger = logging.getLogger(__name__)


# Values (command subcomponents)

def calculate_node_count(task: Task, inputs: List[str]):
    node_count = min(len(inputs), task.agent.max_nodes)
    return 1 if task.agent.launcher else (node_count if inputs is not None and not task.agent.job_array else 1)


def calculate_walltime(task: Task, options: TaskOptions, inputs: List[str]):
    # TODO: refactor (https://github.com/Computational-Plant-Science/plantit/issues/205)
    # adjust based on number of input files and parallelism [requested walltime * input files / nodes]
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

    # if a time limit was requested at submission time, use that
    if task.time_limit is not None:
        requested = task.time_limit
        limit_type = 'user-requested'
    else:
        # otherwise use the default time limit from the workflow configuration
        jobqueue = options['jobqueue']
        spl = jobqueue['walltime' if 'walltime' in jobqueue else 'time'].split(':')
        hours = int(spl[0])
        minutes = int(spl[1])
        seconds = int(spl[2])
        requested = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        limit_type = 'workflow-default'

    # round to the nearest hour, making sure not to exceed agent's maximum, then convert to HH:mm:ss string
    requested_hours = ceil(requested.total_seconds() / 60 / 60)
    permitted_hours = ceil(task.agent.max_time.total_seconds() / 60 / 60)
    hours = requested_hours if requested_hours <= permitted_hours else permitted_hours
    hours = '1' if hours == 0 else f"{hours}"  # if we rounded down to zero, bump to 1
    if len(hours) == 1: hours = f"0{hours}"
    walltime = f"{hours}:00:00"

    logger.info(f"Using {limit_type} walltime {walltime} for {task.user.username}'s task {task.guid}")
    return walltime


# Commands (script subcomponents)

def compose_pull_headers(task: Task) -> List[str]:
    headers = []
    workdir = join(task.agent.workdir, task.workdir)

    # memory
    if not has_virtual_memory(task.agent):
        headers.append(f"#SBATCH --mem=1GB")

    # walltime
    walltime = settings.PULL_JOB_WALLTIME
    headers.append(f"#SBATCH --time={walltime}")  # TODO: calculate as a function of input size?

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
    headers.append(f"#SBATCH --output={join(workdir, 'plantit.%j.pull.out')}")
    headers.append(f"#SBATCH --error={join(workdir, 'plantit.%j.pull.err')}")

    return headers


def compose_pull_commands(task: Task, options: TaskOptions) -> List[str]:
    commands = []
    workdir = join(task.agent.workdir, task.workdir)
    commands.append(f"cd {workdir}")

    # job arrays may cause an invalid singularity cache due to lots of simultaneous pulls of the same image...
    # just pull it once ahead of time so it's already cached
    # TODO: set the image path to the cached one
    workflow_image = options['image']
    workflow_shell = options.get('shell', None)
    if workflow_shell is None: workflow_shell = 'sh'
    pull_image_command = f"singularity exec {workflow_image} {workflow_shell} -c 'echo \"refreshing {workflow_image}\"'"
    commands.append(pull_image_command)

    # make sure we have inputs
    if 'input' not in options: return commands
    input = options['input']
    if input is None: return []

    # singularity must be pre-authenticated on the agent, e.g. with `singularity remote login --username <your username> docker://docker.io`
    # also, if this is a job array, all jobs will invoke iget, but files will only be downloaded once (since we don't use -f for force)
    input_path = input['path']
    workdir = join(workdir, 'input')
    icommands_image = f"docker://{settings.ICOMMANDS_IMAGE}"
    pull_data_command = f"singularity exec {icommands_image} iget -r {input_path} {workdir}"
    commands.append(pull_data_command)

    newline = '\n'
    logger.debug(f"Using pull command: {newline.join(commands)}")
    return commands


def compose_job_headers(task: Task, options: TaskOptions, inputs: List[str]) -> List[str]:
    if 'jobqueue' not in options: return []
    jobqueue = options['jobqueue']
    headers = []
    workdir = join(task.agent.workdir, task.workdir)

    # memory
    if ('memory' in jobqueue or 'mem' in jobqueue) and not has_virtual_memory(task.agent):
        memory = int((jobqueue['memory'] if 'memory' in jobqueue else jobqueue['mem']).replace('GB', ''))
        memory = min(memory, task.agent.max_mem)
        headers.append(f"#SBATCH --mem={str(memory)}GB")

    # walltime
    if 'walltime' in jobqueue or 'time' in jobqueue:
        walltime = calculate_walltime(task, options, inputs)
        # task.job_requested_walltime = walltime
        # task.save()
        headers.append(f"#SBATCH --time={walltime}")

    # queue/partition
    # if task.agent.orchestrator_queue is not None and task.agent.orchestrator_queue != '':
    #     headers.append(f"#SBATCH --partition={task.agent.orchestrator_queue}")
    # else:
    #     headers.append(f"#SBATCH --partition={task.agent.queue}")
    headers.append(f"#SBATCH --partition={task.agent.queue}")

    # allocation
    if task.agent.project is not None and task.agent.project != '':
        headers.append(f"#SBATCH -A {task.agent.project}")

    # cores per task
    if 'cores' in jobqueue:
        headers.append(f"#SBATCH -c {min(int(jobqueue['cores']), task.agent.max_cores)}")

    # nodes & tasks per node
    if len(inputs) > 0 and options['input']['kind'] == 'files':
        nodes = calculate_node_count(task, inputs)
        tasks = min(len(inputs), task.agent.max_tasks)
        # if task.agent.job_array: headers.append(f"#SBATCH --array=1-{len(inputs)}")
        headers.append(f"#SBATCH -N {nodes}")
        headers.append(f"#SBATCH --ntasks={tasks}")
    else:
        headers.append("#SBATCH -N 1")
        headers.append("#SBATCH --ntasks=1")

    # gpus
    gpus = options['gpus'] if 'gpus' in options else 0
    if gpus:
        headers.append(f"#SBATCH --gres=gpu:{gpus}")

    # email notifications
    headers.append("#SBATCH --mail-type=END,FAIL")
    headers.append(f"#SBATCH --mail-user={task.user.email}")

    # log files
    headers.append(f"#SBATCH --output={join(workdir, 'plantit.%j.out')}")
    headers.append(f"#SBATCH --error={join(workdir, 'plantit.%j.err')}")

    newline = '\n'
    logger.debug(f"Using headers: {newline.join(headers)}")
    return headers


def compose_job_commands(task: Task, options: TaskOptions) -> List[str]:
    commands = []
    workdir = join(task.agent.workdir, task.workdir)
    commands.append(f"cd {workdir}")

    # if this agent uses TACC's launcher, use a parameter sweep script
    if task.agent.launcher:
        commands.append(f"export LAUNCHER_WORKDIR={workdir}")
        commands.append(f"export LAUNCHER_JOB_FILE={os.environ.get('LAUNCHER_SCRIPT_NAME')}")
        commands.append("$LAUNCHER_DIR/paramrun")
    # otherwise use SLURM job arrays
    else:
        image = options['image']
        command = options['command']
        env = options['env']
        # TODO: if workflow is configured for gpu, use the number of gpus configured on the agent
        gpus = options['gpus'] if 'gpus' in options else 0
        parameters = (options['parameters'] if 'parameters' in options else []) + [
            Parameter(key='OUTPUT', value=options['output']['from']),
            Parameter(key='GPUS', value=str(gpus))]
        bind_mounts = options['mount'] if ('mount' in options and isinstance(options['mount'], list)) else []
        no_cache = options['no_cache'] if 'no_cache' in options else False
        shell = options['shell'] if 'shell' in options else None

        # for any bind mounts, create eponymous subdirectories of the working directory
        for mount in bind_mounts:
            commands.append(f"mkdir -p {join(workdir, mount['host_path'])}")

        if 'input' in options:
            input_kind = options['input']['kind']
            input_dir_name = options['input']['path'].rpartition('/')[2]

            if input_kind == 'files' or input_kind == 'file':
                input_path = join(workdir, 'input', input_dir_name, '$file') if input_kind == 'files' else join(workdir, 'input', '$file')
                parameters = parameters + [Parameter(key='INPUT', value=input_path), Parameter(key='INDEX', value='$SLURM_ARRAY_TASK_ID')]
                commands.append(f"file=$(head -n $SLURM_ARRAY_TASK_ID {join(workdir, settings.INPUTS_FILE_NAME)} | tail -1)")
            elif options['input']['kind'] == 'directory':
                input_path = join(workdir, 'input', input_dir_name)
                parameters = parameters + [Parameter(key='INPUT', value=input_path)]
            else: raise ValueError(f"Unsupported \'input.kind\': {input_kind}")

        commands = commands + compose_singularity_invocation(
            work_dir=workdir,
            image=image,
            commands=command,
            env=env,
            parameters=parameters,
            bind_mounts=bind_mounts,
            no_cache=no_cache,
            gpus=gpus,
            shell=shell)

    newline = '\n'
    logger.debug(f"Using container commands: {newline.join(commands)}")
    return commands


def compose_push_headers(task: Task) -> List[str]:
    headers = []
    workdir = join(task.agent.workdir, task.workdir)

    # memory
    if not has_virtual_memory(task.agent):
        headers.append(f"#SBATCH --mem=1GB")

    # walltime
    # TODO: calculate as a function of number/size of output files?
    walltime = settings.PUSH_JOB_WALLTIME
    headers.append(f"#SBATCH --time={walltime}")

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
    headers.append(f"#SBATCH --output={join(workdir, 'plantit.%j.push.out')}")
    headers.append(f"#SBATCH --error={join(workdir, 'plantit.%j.push.err')}")

    return headers


def compose_push_commands(task: Task, options: TaskOptions) -> List[str]:
    commands = []
    workdir = join(task.agent.workdir, task.workdir)
    commands.append(f"cd {workdir}")

    # create staging directory
    staging_dir = join(workdir, f"{task.guid}_staging")
    mkdir_command = f"mkdir -p {staging_dir}"
    commands.append(mkdir_command)

    # create zip directory
    zip_dir = join(staging_dir, f"{task.guid}_zip")
    mkdir_command = f"mkdir -p {zip_dir}"
    commands.append(mkdir_command)

    # copy output files to staging directory
    output = options['output']
    if 'include' in output:
        cp_cmd = f"cp -t "

        # exact matches
        if 'names' in output['include']:
            for name in output['include']['names']:
                path = join(workdir, name)
                trap_msg = f"echo 'No included names to move'"
                commands.append(f"{cp_cmd} {staging_dir} {path} || {trap_msg}")
                commands.append(f"{cp_cmd} {zip_dir} {path} || {trap_msg}")

        # glob matches
        if 'patterns' in output['include']:
            for pattern in (list(output['include']['patterns'])):
                pattern = join(workdir, f"**{pattern}*")
                trap_msg = f"echo 'No included patterns to move'"
                commands.append(f"{cp_cmd} {staging_dir} {pattern} || {trap_msg}")
                commands.append(f"{cp_cmd} {zip_dir} {pattern} || {trap_msg}")

        # include all scheduler log files in zip file
        for pattern in ['out', 'err']:
            pattern = join(workdir, f"**{pattern}*")
            trap_msg = f"echo 'No log files to move'"
            commands.append(f"{cp_cmd} {staging_dir} {pattern} || {trap_msg}")
            commands.append(f"{cp_cmd} {zip_dir} {pattern} || {trap_msg}")
    else:
        raise ValueError(f"No outputs specified")

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
    zip_name = f"{task.guid}.zip"
    zip_path = join(staging_dir, zip_name)
    zip_command = f"zip -j -r {zip_path} {zip_dir}/*"
    commands.append(zip_command)

    # remove zip dir
    commands.append(f"rm -rf {zip_dir}")

    # transfer contents of staging dir to CyVerse
    to_path = output['to']
    image = f"docker://{settings.ICOMMANDS_IMAGE}"
    # force = output['force']
    force = False
    # just_zip = output['just_zip']
    just_zip = False
    # push_command = f"singularity exec {image} iput -r{' -f ' if force else ' '}{staging_dir}{('/' + zip_name) if just_zip else '/*'} {to_path}/"
    push_command = f"singularity exec {image} iput -f {staging_dir}{('/' + zip_name) if just_zip else '/*'} {to_path}/"
    commands.append(push_command)

    newline = '\n'
    logger.debug(f"Using push commands: {newline.join(commands)}")
    return commands


def compose_report_headers(task: Task) -> List[str]:
    headers = []
    workdir = join(task.agent.workdir, task.workdir)

    # memory
    if not has_virtual_memory(task.agent):
        headers.append(f"#SBATCH --mem=1GB")

    # walltime
    headers.append(f"#SBATCH --time=00:10:00")

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
    headers.append(f"#SBATCH --output={join(workdir, 'plantit.%j.report.out')}")
    headers.append(f"#SBATCH --error={join(workdir, 'plantit.%j.report.err')}")

    return headers


def compose_report_commands(task: Task) -> List[str]:
    image = f"docker://{settings.CURL_IMAGE}"
    return [
        f"singularity exec {image} curl -L -v -X POST {settings.API_URL}/tasks/{task.guid}/complete/"
    ]


# Job scripts

def compose_pull_script(task: Task, options: TaskOptions) -> List[str]:
    with open(settings.TASKS_TEMPLATE_SCRIPT_SLURM, 'r') as template_file:
        template = [line.strip() for line in template_file if line != '']
        headers = compose_pull_headers(task)
        command = compose_pull_commands(task, options)
        return template + \
               headers + \
               [task.agent.pre_commands] + \
               command


def compose_job_script(task: Task, options: TaskOptions, inputs: List[str]) -> List[str]:
    with open(settings.TASKS_TEMPLATE_SCRIPT_SLURM, 'r') as template_file:
        template = [line.strip() for line in template_file if line != '']
        headers = compose_job_headers(task, options, inputs)
        command = compose_job_commands(task, options)
        return template + \
               headers + \
               [task.agent.pre_commands] + \
               command


def compose_push_script(task: Task, options: TaskOptions) -> List[str]:
    with open(settings.TASKS_TEMPLATE_SCRIPT_SLURM, 'r') as template_file:
        template = [line.strip() for line in template_file if line != '']
        headers = compose_push_headers(task)
        command = compose_push_commands(task, options)
        return template + \
               headers + \
               [task.agent.pre_commands] + \
               command


def compose_report_script(task: Task) -> List[str]:
    with open(settings.TASKS_TEMPLATE_SCRIPT_SLURM, 'r') as template_file:
        template = [line.strip() for line in template_file if line != '']
        headers = compose_report_headers(task)
        command = compose_report_commands(task)
        return template + \
               headers + \
               [task.agent.pre_commands] + \
               command


def compose_launcher_script(task: Task, options: TaskOptions, inputs: List[str]) -> List[str]:
    workdir = join(task.agent.workdir, task.workdir)
    lines: List[str] = []
    image = options['image']
    command = options['command']
    env = options['env']
    gpus = options[
        'gpus'] if 'gpus' in options else 0  # TODO: if workflow is configured for gpu, use the number of gpus configured on the agent
    parameters = (options['parameters'] if 'parameters' in options else []) + [
        Parameter(key='OUTPUT', value=options['output']['from']),
        Parameter(key='GPUS', value=str(gpus))]
    bind_mounts = options['mount'] if ('mount' in options and isinstance(options['mount'], list)) else []
    no_cache = options['no_cache'] if 'no_cache' in options else False
    shell = options['shell'] if 'shell' in options else None

    if 'input' in options:
        input_kind = options['input']['kind']
        input_dir_name = options['input']['path'].rpartition('/')[2]

        if input_kind == 'files':
            for i, file_name in enumerate(inputs):
                input_path = join(workdir, 'input', input_dir_name, file_name)
                lines = lines + compose_singularity_invocation(
                    work_dir=workdir,
                    image=image,
                    commands=command,
                    env=env,
                    parameters=parameters + [Parameter(key='INPUT', value=input_path)],
                    bind_mounts=bind_mounts,
                    no_cache=no_cache,
                    gpus=gpus,
                    shell=shell,
                    index=i)
            return lines
        elif input_kind == 'directory':
            input_path = join(workdir, 'input', input_dir_name)
            parameters = parameters + [Parameter(key='INPUT', value=input_path)]
        elif input_kind == 'file':
            input_path = join(workdir, 'input', inputs[0])
            parameters = parameters + [Parameter(key='INPUT', value=input_path)]
        else: raise ValueError(f"Unsupported \'input.kind\': {input_kind}")
    elif 'iterations' in options:
        iterations = options['iterations']
        for i in range(0, iterations):
            lines = lines + compose_singularity_invocation(
                work_dir=workdir,
                image=image,
                commands=command,
                env=env,
                parameters=parameters,
                bind_mounts=bind_mounts,
                no_cache=no_cache,
                gpus=gpus,
                shell=shell,
                index=i)
        return lines

    return lines + compose_singularity_invocation(
        work_dir=workdir,
        image=image,
        commands=command,
        env=env,
        parameters=parameters,
        bind_mounts=bind_mounts,
        no_cache=no_cache,
        gpus=gpus,
        shell=shell)
