import traceback
from os import environ
from os.path import join
from typing import List

import requests
import yaml
from celery.utils.log import get_task_logger
from django.utils import timezone
from requests import RequestException, Timeout, ReadTimeout, HTTPError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from plantit import settings
from plantit.celery import app
from plantit.collections.models import CollectionSession
from plantit.collections.utils import update_collection_session
from plantit.options import FilesInput, FileInput, Parameter
from plantit.runs.cluster import get_job_status, get_job_walltime
from plantit.runs.models import Run
from plantit.runs.ssh import SSH
from plantit.runs.utils import update_status, execute_command, map_old_workflow_config_to_new, remove_logs, parse_job_id, create_run
from plantit.clusters.models import Cluster
from plantit.utils import parse_run_options, prep_run_command

logger = get_task_logger(__name__)


def __upload_run(flow, run: Run, ssh: SSH, input_files: List[str] = None):
    # update flow config before uploading
    flow['config']['workdir'] = join(run.cluster.workdir, run.guid)
    flow['config']['log_file'] = f"{run.guid}.{run.cluster.name.lower()}.log"
    if 'output' in flow['config']:
        flow['config']['output']['from'] = join(run.cluster.workdir, run.work_dir, flow['config']['output']['from'])

    # if flow has outputs, make sure we don't push configuration or job scripts
    if 'output' in flow['config']:
        flow['config']['output']['exclude']['names'] = [
            "flow.yaml",
            "template_local_run.sh",
            "template_slurm_run.sh"]

    resources = None if 'resources' not in flow['config']['cluster'] else flow['config']['cluster']['resources']  # cluster resource requests, if any
    callback_url = settings.API_URL + 'runs/' + run.guid + '/status/'  # PlantIT status update callback URL
    work_dir = join(run.cluster.workdir, run.work_dir)
    new_flow = map_old_workflow_config_to_new(flow, run, resources)  # TODO update flow UI page

    # create working directory
    execute_command(ssh_client=ssh, pre_command=':', command=f"mkdir {work_dir}", directory=run.cluster.workdir, allow_stderr=True)

    # upload flow config and job script
    with ssh.client.open_sftp() as sftp:
        sftp.chdir(work_dir)

        # TODO refactor to allow multiple cluster schedulers
        sandbox = run.cluster.name == 'Sandbox'  # for now, we're either in the sandbox or on a SLURM cluster
        template = environ.get('CELERY_TEMPLATE_LOCAL_RUN_SCRIPT') if sandbox else environ.get('CELERY_TEMPLATE_SLURM_RUN_SCRIPT')
        template_name = template.split('/')[-1]

        # upload flow config file
        with sftp.open('flow.yaml', 'w') as flow_file:
            if run.cluster.launcher:
                del new_flow['jobqueue']
            yaml.dump(new_flow, flow_file, default_flow_style=False)

        # compose and upload job script
        with open(template, 'r') as template_script, sftp.open(template_name, 'w') as script:
            print(f"Uploading {template_name}")
            for line in template_script:
                script.write(line)

            if not sandbox:
                # we're on a SLURM cluster, so add resource requests
                script.write("#SBATCH --ntasks=1\n")

                if 'cores' in resources:
                    script.write(f"#SBATCH --cpus-per-task={resources['cores']}\n")
                if 'time' in resources:
                    script.write(f"#SBATCH --time={resources['time']}\n")
                if 'mem' in resources and (run.cluster.header_skip is None or '--mem' not in str(run.cluster.header_skip)):
                    script.write(f"#SBATCH --mem={resources['mem']}\n")
                if run.cluster.queue is not None and run.cluster.queue != '':
                    script.write(f"#SBATCH --partition={run.cluster.queue}\n")
                if run.cluster.project is not None and run.cluster.project != '':
                    script.write(f"#SBATCH -A {run.cluster.project}\n")

                input_count = len(input_files)
                if input_files is not None and run.cluster.no_nested:
                    script.write(f"#SBATCH --array=1-{input_count}\n")
                if input_files is not None:
                    script.write(f"#SBATCH -N {min(input_count, run.cluster.max_nodes)}\n")
                else:
                    script.write(f"#SBATCH -N 1\n")

                script.write("#SBATCH --mail-type=END,FAIL\n")
                script.write(f"#SBATCH --mail-user={run.user.email}\n")
                script.write("#SBATCH --output=plantit.%j.out\n")
                script.write("#SBATCH --error=plantit.%j.err\n")

            # add precommands
            script.write(run.cluster.pre_commands + '\n')

            # if we have inputs, add pull command
            if 'input' in flow['config']:
                sftp.mkdir(join(run.cluster.workdir, run.work_dir, 'input'))
                pull_commands = f"plantit terrain pull {flow['config']['input']['from']}" \
                                f" -p {join(run.cluster.workdir, run.work_dir, 'input')}" \
                                f" {' '.join(['--pattern ' + pattern for pattern in flow['config']['input']['patterns']])}" \
                                f""f" --plantit_url '{callback_url}'" \
                                f""f" --plantit_token '{run.token}'" \
                                f""f" --terrain_token {run.user.profile.cyverse_token}\n"
                logger.info(f"Using pull command: {pull_commands}")
                script.write(pull_commands)

            docker_username = environ.get('DOCKER_USERNAME', None)
            docker_password = environ.get('DOCKER_PASSWORD', None)

            # if this cluster uses TACC's launcher, create a parameter sweep launcher job script to invoke singularity directly
            if run.cluster.launcher and input_files is not None:
                with sftp.open('launch', 'w') as launcher_script:
                    for file in input_files:
                        parse_errors, run_options = parse_run_options(new_flow)
                        if len(parse_errors) > 0:
                            raise ValueError(f"Failed to parse run options: {' '.join(parse_errors)}")
                        file_name = file.rpartition('/')[2]
                        run_options.input = FileInput(file_name)
                        command = prep_run_command(
                            work_dir=run_options.workdir,
                            image=run_options.image,
                            command=run_options.command,
                            parameters=(run_options.parameters if run_options.parameters is not None else []) + [
                                Parameter(key='INPUT', value=join(run.cluster.workdir, run.work_dir, 'input', file_name))],
                            bind_mounts=run_options.bind_mounts,
                            docker_username=docker_username,
                            docker_password=docker_password,
                            no_cache=run_options.no_cache,
                            gpu=run_options.gpu)
                        launcher_script.write(f"{command}\n")

                script.write(f"export LAUNCHER_WORKDIR={join(run.cluster.workdir, run.work_dir)}\n")
                script.write(f"export LAUNCHER_JOB_FILE=launch\n")
                script.write("$LAUNCHER_DIR/paramrun\n")
            # otherwise use the CLI
            else:
                run_commands = f"plantit run flow.yaml --plantit_url '{callback_url}' --plantit_token '{run.token}' --pre_pull_image"
                if run.cluster.no_nested and input_files is not None:
                    run_commands += f" --slurm_job_array"

                if docker_username is not None and docker_password is not None:
                    run_commands += f" --docker_username {docker_username} --docker_password {docker_password}"

                run_commands += "\n"
                logger.info(f"Using run command: {run_commands}")
                script.write(run_commands)

            # if we have outputs...
            if 'output' in flow:
                # add zip command
                zip_commands = f"plantit zip {flow['output']['from']}"
                if 'include' in flow['output']:
                    if 'patterns' in flow['output']['include']:
                        zip_commands = zip_commands + ' '.join(['--include_pattern ' + pattern for pattern in flow['output']['include']['patterns']])
                    if 'names' in flow['output']['include']:
                        zip_commands = zip_commands + ' '.join(['--include_name ' + pattern for pattern in flow['output']['include']['names']])
                    if 'patterns' in flow['output']['exclude']:
                        zip_commands = zip_commands + ' '.join(['--exclude_pattern ' + pattern for pattern in flow['output']['exclude']['patterns']])
                    if 'names' in flow['output']['exclude']:
                        zip_commands = zip_commands + ' '.join(['--exclude_name ' + pattern for pattern in flow['output']['exclude']['names']])
                zip_commands += '\n'
                logger.info(f"Using zip command: {zip_commands}")

                # add push command if we have a destination
                if 'to' in flow['output']:
                    push_commands = f"plantit terrain push {flow['output']['to']}" \
                                    f" -p {join(run.work_dir, flow['output']['from'])}" \
                                    f" --plantit_url '{callback_url}'" \
                                    f" --plantit_token '{run.token}'" \
                                    f" --terrain_token {run.user.profile.cyverse_token}"
                    if 'include' in flow['output']:
                        if 'patterns' in flow['output']['include']:
                            push_commands = push_commands + ' '.join(
                                ['--include_pattern ' + pattern for pattern in flow['output']['include']['patterns']])
                        if 'names' in flow['output']['include']:
                            push_commands = push_commands + ' '.join(['--include_name ' + pattern for pattern in flow['output']['include']['names']])
                        if 'patterns' in flow['output']['exclude']:
                            push_commands = push_commands + ' '.join(
                                ['--exclude_pattern ' + pattern for pattern in flow['output']['exclude']['patterns']])
                        if 'names' in flow['output']['exclude']:
                            push_commands = push_commands + ' '.join(['--exclude_name ' + pattern for pattern in flow['output']['exclude']['names']])
                    push_commands += '\n'
                    script.write(push_commands)
                    logger.info(f"Using push command: {push_commands}")


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(ConnectionError) | retry_if_exception_type(
        RequestException) | retry_if_exception_type(ReadTimeout) | retry_if_exception_type(
        Timeout) | retry_if_exception_type(HTTPError)))
def __list_dir(path: str, token: str) -> List[str]:
    with requests.get(
            f"https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path={path}",
            headers={'Authorization': f"Bearer {token}"}) as response:
        if response.status_code == 500 and response.json()['error_code'] == 'ERR_DOES_NOT_EXIST':
            raise ValueError(f"Path {path} does not exist")

        response.raise_for_status()
        content = response.json()
        files = content['files']
        return [file['path'] for file in files]


def __submit_run(flow, run: Run, ssh: SSH, file_count: int = None):
    # TODO refactor to allow multiple cluster schedulers
    sandbox = run.cluster.name == 'Sandbox'  # for now, we're either in the sandbox or on a SLURM cluster
    template = environ.get('CELERY_TEMPLATE_LOCAL_RUN_SCRIPT') if sandbox else environ.get('CELERY_TEMPLATE_SLURM_RUN_SCRIPT')
    template_name = template.split('/')[-1]

    if run.is_sandbox:
        execute_command(
            ssh_client=ssh,
            pre_command='; '.join(str(run.cluster.pre_commands).splitlines()) if run.cluster.pre_commands else ':',
            command=f"chmod +x {template_name} && ./{template_name}",
            directory=join(run.cluster.workdir, run.work_dir),
            allow_stderr=True)
    else:
        # command = f"chmod +x {template_name} && ./{template_name}" if run.cluster.no_nested else f"chmod +x {template_name} && sbatch {template_name}"
        command = f"chmod +x {template_name} && sbatch {template_name}"
        output_lines = execute_command(
            ssh_client=ssh,
            pre_command='; '.join(str(run.cluster.pre_commands).splitlines()) if run.cluster.pre_commands else ':',
            # if the cluster scheduler prohibits nested job submissions, we need to run the CLI from a login node
            command=command,
            directory=join(run.cluster.workdir, run.work_dir),
            allow_stderr=True)
        job_id = parse_job_id(output_lines[-1])
        run.job_id = job_id
        run.updated = timezone.now()
        run.save()


@app.task(track_started=True)
def create_and_submit_run(username: str, cluster_name: str, flow: dict):
    run = create_run(username, cluster_name, flow)
    submit_run.s(run.guid, flow).apply_async()


@app.task(track_started=True)
def submit_run(id: str, flow):
    run = Run.objects.get(guid=id)
    run.job_status = 'RUNNING'
    run.submission_id = submit_run.request.id  # set this task's ID on the run so user can cancel it
    run.save()

    msg = f"Deploying run {run.guid} to {run.cluster.name}"
    update_status(run, msg)
    logger.info(msg)

    try:
        if 'auth' in flow:
            msg = f"Authenticating with username {flow['auth']['username']}"
            update_status(run, msg)
            logger.info(msg)
            ssh_client = SSH(run.cluster.hostname, run.cluster.port, flow['auth']['username'], flow['auth']['password'])
        else:
            ssh_client = SSH(run.cluster.hostname, run.cluster.port, run.cluster.username)

        with ssh_client:
            msg = f"Creating working directory {join(run.cluster.workdir, run.guid)} and uploading workflow configuration"
            update_status(run, msg)
            logger.info(msg)

            if 'input' in flow['config'] and flow['config']['input']['kind'] == 'files':
                input_files = __list_dir(flow['config']['input']['from'], run.user.profile.cyverse_token)
                msg = f"Found {len(input_files)} input files"
                update_status(run, msg)
                logger.info(msg)
            else:
                input_files = None

            __upload_run(flow, run, ssh_client, input_files)

            msg = 'Running script' if run.is_sandbox else 'Submitting script to scheduler'
            update_status(run, msg)
            logger.info(msg)

            __submit_run(flow, run, ssh_client, len(input_files) if input_files is not None else None)

            if run.is_sandbox:
                run.job_status = 'SUCCESS'
                now = timezone.now()
                run.updated = now
                run.completed = now
                run.save()

                cleanup_delay = int(environ.get('RUNS_CLEANUP_MINUTES'))
                msg = f"Completed run {run.guid}, cleaning up in {cleanup_delay}m"
                update_status(run, msg)
                logger.info(msg)
                cleanup_run.s(id).apply_async(countdown=cleanup_delay * 60)
            else:
                delay = int(environ.get('RUNS_REFRESH_SECONDS'))
                update_status(run, f"Polling for job status in {delay}s")
                poll_run_status.s(run.guid).apply_async(countdown=delay)
    except Exception:
        run.job_status = 'FAILURE'
        now = timezone.now()
        run.updated = now
        run.completed = now
        run.save()

        msg = f"Failed to submit run {run.guid}: {traceback.format_exc()}."
        update_status(run, msg)
        logger.error(msg)


@app.task()
def poll_run_status(id: str):
    run = Run.objects.get(guid=id)
    refresh_delay = int(environ.get('RUNS_REFRESH_SECONDS'))
    cleanup_delay = int(environ.get('RUNS_CLEANUP_MINUTES'))

    logger.info(f"Checking {run.cluster.name} scheduler status for run {id} (SLURM job {run.job_id})")

    # if the job already failed, schedule cleanup
    if run.job_status == 'FAILURE':
        update_status(run, f"Job {run.job_id} already failed, cleaning up in {cleanup_delay}m")
        cleanup_run.s(id).apply_async(countdown=cleanup_delay)

    # otherwise poll the scheduler for its status
    try:
        job_status = get_job_status(run)
        job_walltime = get_job_walltime(run)
        run.job_status = job_status
        run.job_walltime = job_walltime

        now = timezone.now()
        run.updated = now
        run.save()

        if job_status == 'COMPLETED' or job_status == 'FAILED' or job_status == 'CANCELLED' or job_status == 'TIMEOUT':
            run.completed = now
            run.save()

            msg = f"Job {run.job_id} {job_status}" + (
                f" after {job_walltime}" if job_walltime is not None else '') + f", cleaning up in {int(environ.get('RUNS_CLEANUP_MINUTES'))}m"
            update_status(run, msg)
            cleanup_run.s(id).apply_async(countdown=cleanup_delay)
        else:
            msg = f"Job {run.job_id} {job_status}, walltime {job_walltime}, polling again in {refresh_delay}s"
            update_status(run, msg)
            poll_run_status.s(id).apply_async(countdown=refresh_delay)
    except StopIteration:
        if not (run.job_status == 'COMPLETED' or run.job_status == 'COMPLETING'):
            run.job_status = 'FAILURE'
            now = timezone.now()
            run.updated = now
            run.completed = now
            run.save()

            msg = f"Job {run.job_id} not found, cleaning up in {int(environ.get('RUNS_CLEANUP_MINUTES'))}m"
            update_status(run, msg)
        else:
            update_status(run, f"Job {run.job_id} already succeeded, cleaning up in {int(environ.get('RUNS_CLEANUP_MINUTES'))}m")
            cleanup_run.s(id).apply_async(countdown=cleanup_delay)
    except:
        run.job_status = 'FAILURE'
        now = timezone.now()
        run.updated = now
        run.completed = now
        run.save()

        msg = f"Job {run.job_id} encountered unexpected error (cleaning up in {int(environ.get('RUNS_CLEANUP_MINUTES'))}m): {traceback.format_exc()}"
        update_status(run, msg)
        cleanup_run.s(id).apply_async(countdown=cleanup_delay)


@app.task()
def cleanup_run(id: str):
    try:
        run = Run.objects.get(guid=id)
    except:
        logger.info(f"Could not find run {id} (might have been deleted?)")
        return

    logger.info(f"Cleaning up run {id} local working directory {run.cluster.workdir}")
    remove_logs(run.guid, run.cluster.name)
    logger.info(f"Cleaning up run {id} cluster working directory {run.cluster.workdir}")
    ssh = SSH(run.cluster.hostname, run.cluster.port, run.cluster.username)
    with ssh:
        execute_command(
            ssh_client=ssh,
            pre_command=run.cluster.pre_commands,
            command=f"rm -r {join(run.cluster.workdir, run.work_dir)}",
            directory=run.cluster.workdir,
            allow_stderr=True)
    run.delete()


@app.task()
def clean_singularity_cache(cluster_name: str):
    cluster_name = Cluster.objects.get(name=cluster_name)
    ssh = SSH(cluster_name.hostname, cluster_name.port, cluster_name.username)
    with ssh:
        execute_command(
            ssh_client=ssh,
            pre_command=cluster_name.pre_commands,
            command="singularity cache clean",
            directory=cluster_name.workdir,
            allow_stderr=True)


@app.task()
def run_command(cluster_name: str, command: str, pre_command: str = None):
    cluster = Cluster.objects.get(name=cluster_name)
    ssh = SSH(cluster.hostname, cluster.port, cluster.username)
    with ssh:
        lines = execute_command(
            ssh_client=ssh,
            pre_command=cluster.pre_commands + '' if pre_command is None else f"&& {pre_command}",
            command=command,
            directory=cluster.workdir,
            allow_stderr=True)


@app.task()
def open_collection_session(id: str):
    try:
        session = CollectionSession.objects.get(guid=id)
        ssh_client = SSH(session.cluster.hostname, session.cluster.port, session.cluster.username)

        with ssh_client:
            msg = f"Creating working directory {session.workdir}"
            update_collection_session(session, [f"Creating working directory {session.workdir}"])
            logger.info(msg)

            execute_command(
                ssh_client=ssh_client,
                pre_command=':',
                command=f"mkdir {session.guid}/",
                directory=session.cluster.workdir)

            msg = f"Transferring files from {session.path} to {session.cluster.name}"
            update_collection_session(session, [msg])
            logger.info(msg)

            command = f"plantit terrain pull {session.path} --terrain_token {session.user.profile.cyverse_token}\n"
            lines = execute_command(
                ssh_client=ssh_client,
                pre_command=session.cluster.pre_commands,
                command=command,
                directory=session.workdir,
                allow_stderr=True)
            update_collection_session(session, lines)

            session.opening = False
            session.save()
            msg = f"Succesfully opened collection"
            update_collection_session(session, [msg])
            logger.info(msg)
    except:
        msg = f"Failed to open session: {traceback.format_exc()}."
        logger.error(msg)


@app.task()
def save_collection_session(id: str, only_modified: bool):
    try:
        session = CollectionSession.objects.get(guid=id)

        msg = f"Saving collection session {session.guid} on {session.cluster.name}"
        update_collection_session(session, [msg])
        logger.info(msg)

        ssh_client = SSH(session.cluster.hostname, session.cluster.port, session.cluster.username)

        with ssh_client:
            msg = f"Transferring {'modified' if only_modified else 'all'} files from {session.cluster.name} to {session.path}"
            update_collection_session(session, [msg])
            logger.info(msg)

            command = f"plantit terrain push {session.path} --terrain_token {session.user.profile.cyverse_token}"
            for file in session.modified:
                command += f" --include_name {file}"

            lines = execute_command(
                ssh_client=ssh_client,
                pre_command=session.cluster.pre_commands,
                command=command,
                directory=session.workdir,
                allow_stderr=True)
            update_collection_session(session, lines)
    except:
        msg = f"Failed to open session: {traceback.format_exc()}."
        logger.error(msg)


@app.task()
def close_collection_session(id: str):
    pass
