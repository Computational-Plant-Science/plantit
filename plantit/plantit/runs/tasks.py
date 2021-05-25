import base64
import fileinput
import json
import sys
import tempfile
import traceback
from os import environ
from os.path import join

import cv2
from celery.utils.log import get_task_logger
from czifile import czifile
from django.contrib.auth.models import User
from django.utils import timezone
from preview_generator.exception import UnsupportedMimeType
from preview_generator.manager import PreviewManager

from plantit import settings
from plantit.celery import app
from plantit.datasets.models import DatasetSession
from plantit.datasets.utils import update_dataset_session
from plantit.redis import RedisClient
from plantit.agents.models import Agent
from plantit.runs.models import Run
from plantit.runs.utils import update_run_status, remove_logs, create_run, \
    get_run_container_log_file_name, get_run_container_log_file_path, get_run_results, get_run_job_walltime, get_run_job_status, submit_run_via_ssh, \
    upload_run
from plantit.ssh import SSH, execute_command
from plantit.terrain import list_dir
from plantit.sns import SnsClient
from plantit.workflows.utils import refresh_workflow

logger = get_task_logger(__name__)


@app.task(track_started=True)
def create_and_submit_run(username: str, agent: str, flow: dict):
    run = create_run(username, agent, flow)
    submit_run.s(run.guid, flow).apply_async()


@app.task(track_started=True)
def submit_run(id: str, flow):
    run = Run.objects.get(guid=id)
    run.job_status = 'RUNNING'
    run.submission_id = submit_run.request.id  # set this task's ID on the run so user can cancel it
    run.save()

    msg = f"Deploying run {run.guid} to {run.agent.name}"
    update_run_status(run, msg)
    logger.info(msg)

    try:
        if 'auth' in flow:
            msg = f"Authenticating with username {flow['auth']['username']}"
            update_run_status(run, msg)
            logger.info(msg)
            ssh_client = SSH(run.agent.hostname, run.agent.port, flow['auth']['username'], flow['auth']['password'])
        else:
            ssh_client = SSH(run.agent.hostname, run.agent.port, run.agent.username)

        with ssh_client:
            msg = f"Creating working directory {join(run.agent.workdir, run.guid)} and uploading workflow configuration"
            update_run_status(run, msg)
            logger.info(msg)

            if 'input' in flow['config'] and flow['config']['input']['kind'] == 'files':
                input_files = list_dir(flow['config']['input']['from'], run.user.profile.cyverse_token)
                msg = f"Found {len(input_files)} input files"
                update_run_status(run, msg)
                logger.info(msg)
            else:
                input_files = None

            upload_run(flow, run, ssh_client, input_files)

            msg = 'Running script' if run.is_sandbox else 'Submitting script to scheduler'
            update_run_status(run, msg)
            logger.info(msg)

            submit_run_via_ssh(run, ssh_client, len(input_files) if input_files is not None else None)

            if run.is_sandbox:
                run.job_status = 'SUCCESS'
                now = timezone.now()
                run.updated = now
                run.completed = now
                run.save()
                list_run_results.s(id).apply_async()

                cleanup_delay = int(environ.get('RUNS_CLEANUP_MINUTES'))
                msg = f"Completed run {run.guid}, cleaning up in {cleanup_delay}m"
                update_run_status(run, msg)
                logger.info(msg)
                cleanup_run.s(id).apply_async(countdown=cleanup_delay * 60)

                if run.user.profile.push_notification_status == 'enabled':
                    SnsClient.get().publish_message(run.user.profile.push_notification_topic_arn, f"PlantIT run {run.guid}", msg, {})
            else:
                delay = int(environ.get('RUNS_REFRESH_SECONDS'))
                poll_run_status.s(run.guid).apply_async(countdown=delay)
    except Exception:
        run.job_status = 'FAILURE'
        now = timezone.now()
        run.updated = now
        run.completed = now
        run.save()

        msg = f"Failed to submit run {run.guid}: {traceback.format_exc()}."
        update_run_status(run, msg)
        logger.error(msg)


@app.task()
def poll_run_status(id: str):
    run = Run.objects.get(guid=id)
    refresh_delay = int(environ.get('RUNS_REFRESH_SECONDS'))
    cleanup_delay = int(environ.get('RUNS_CLEANUP_MINUTES')) * 60

    logger.info(f"Checking {run.agent.name} scheduler status for run {id} (SLURM job {run.job_id})")

    # if the job already failed, schedule cleanup
    if run.job_status == 'FAILURE':
        msg = f"Job {run.job_id} failed, cleaning up in {cleanup_delay}m"
        update_run_status(run, msg)
        cleanup_run.s(id).apply_async(countdown=cleanup_delay)

        if run.user.profile.push_notification_status == 'enabled':
            SnsClient.get().publish_message(run.user.profile.push_notification_topic_arn, f"PlantIT run {run.guid}", msg, {})

    # otherwise poll the scheduler for its status
    try:
        job_status = get_run_job_status(run)
        job_walltime = get_run_job_walltime(run)
        run.job_status = job_status
        run.job_elapsed_walltime = job_walltime

        now = timezone.now()
        run.updated = now
        run.save()

        # get container logs
        work_dir = join(run.agent.workdir, run.workdir)
        ssh_client = SSH(run.agent.hostname, run.agent.port, run.agent.username)
        container_log_file = get_run_container_log_file_name(run)
        container_log_path = get_run_container_log_file_path(run)

        with ssh_client:
            with ssh_client.client.open_sftp() as sftp:
                cmd = 'test -e {0} && echo exists'.format(join(work_dir, container_log_file))
                stdin, stdout, stderr = ssh_client.client.exec_command(cmd)

                if not stdout.read().decode().strip() == 'exists':
                    container_logs = []
                else:
                    with open(get_run_container_log_file_path(run), 'a+') as log_file:
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

        if job_status == 'COMPLETED' or job_status == 'FAILED' or job_status == 'CANCELLED' or job_status == 'TIMEOUT':
            run.completed = now
            run.save()
            list_run_results.s(id).apply_async()

            msg = f"Job {run.job_id} {job_status}" + (
                f" after {job_walltime}" if job_walltime is not None else '') + f", cleaning up in {int(environ.get('RUNS_CLEANUP_MINUTES'))}m"
            update_run_status(run, msg)
            cleanup_run.s(id).apply_async(countdown=cleanup_delay)

            if run.user.profile.push_notification_status == 'enabled':
                SnsClient.get().publish_message(run.user.profile.push_notification_topic_arn, f"PlantIT run {run.guid}", msg, {})
        else:
            msg = f"Job {run.job_id} {job_status}, walltime {job_walltime}, polling again in {refresh_delay}s"
            update_run_status(run, msg)
            poll_run_status.s(id).apply_async(countdown=refresh_delay)
    except StopIteration:
        if not (run.job_status == 'COMPLETED' or run.job_status == 'COMPLETING'):
            run.job_status = 'FAILURE'
            now = timezone.now()
            run.updated = now
            run.completed = now
            run.save()

            msg = f"Job {run.job_id} not found, cleaning up in {int(environ.get('RUNS_CLEANUP_MINUTES'))}m"
            update_run_status(run, msg)
        else:
            msg = f"Job {run.job_id} succeeded, cleaning up in {int(environ.get('RUNS_CLEANUP_MINUTES'))}m"
            update_run_status(run, msg)
            cleanup_run.s(id).apply_async(countdown=cleanup_delay)

            if run.user.profile.push_notification_status == 'enabled':
                SnsClient.get().publish_message(run.user.profile.push_notification_topic_arn, f"PlantIT run {run.guid}", msg, {})
    except:
        run.job_status = 'FAILURE'
        now = timezone.now()
        run.updated = now
        run.completed = now
        run.save()

        msg = f"Job {run.job_id} encountered unexpected error (cleaning up in {int(environ.get('RUNS_CLEANUP_MINUTES'))}m): {traceback.format_exc()}"
        update_run_status(run, msg)
        cleanup_run.s(id).apply_async(countdown=cleanup_delay)

        if run.user.profile.push_notification_status == 'enabled':
            SnsClient.get().publish_message(run.user.profile.push_notification_topic_arn, f"PlantIT run {run.guid}", msg, {})


@app.task()
def cleanup_run(id: str):
    try:
        run = Run.objects.get(guid=id)
    except:
        logger.info(f"Could not find run {id} (might have been deleted?)")
        return

    logger.info(f"Cleaning up run {id} local working directory {run.agent.workdir}")
    remove_logs(run.guid, run.agent.name)
    logger.info(f"Cleaning up run {id} remote working directory {run.agent.workdir}")
    ssh = SSH(run.agent.hostname, run.agent.port, run.agent.username)
    with ssh:
        execute_command(
            ssh_client=ssh,
            pre_command=run.agent.pre_commands,
            command=f"rm -r {join(run.agent.workdir, run.workdir)}",
            directory=run.agent.workdir,
            allow_stderr=True)

    run.cleaned_up = True
    run.save()

    msg = f"Cleaned up {run.guid}"
    update_run_status(run, msg)


@app.task()
def clean_singularity_cache(agent_name: str):
    agent = Agent.objects.get(name=agent_name)
    ssh = SSH(agent.hostname, agent.port, agent.username)
    with ssh:
        execute_command(
            ssh_client=ssh,
            pre_command=agent.pre_commands,
            command="singularity cache clean",
            directory=agent.workdir,
            allow_stderr=True)


@app.task()
def run_command(agent_name: str, command: str, pre_command: str = None):
    agent = Agent.objects.get(name=agent_name)
    ssh = SSH(agent.hostname, agent.port, agent.username)
    with ssh:
        lines = execute_command(
            ssh_client=ssh,
            pre_command=agent.pre_commands + '' if pre_command is None else f"&& {pre_command}",
            command=command,
            directory=agent.workdir,
            allow_stderr=True)


@app.task()
def open_dataset_session(id: str):
    try:
        session = DatasetSession.objects.get(guid=id)
        ssh = SSH(session.agent.hostname, session.agent.port, session.agent.username)

        with ssh:
            msg = f"Creating working directory {session.workdir}"
            update_dataset_session(session, [f"Creating working directory {session.workdir}"])
            logger.info(msg)

            execute_command(
                ssh_client=ssh,
                pre_command=':',
                command=f"mkdir {session.guid}/",
                directory=session.agent.workdir)

            msg = f"Transferring files from {session.path} to {session.agent.name}"
            update_dataset_session(session, [msg])
            logger.info(msg)

            command = f"plantit terrain pull \"{session.path}\" --terrain_token {session.user.profile.cyverse_token}\n"
            lines = execute_command(
                ssh_client=ssh,
                pre_command=session.agent.pre_commands,
                command=command,
                directory=session.workdir,
                allow_stderr=True)
            update_dataset_session(session, lines)

            session.opening = False
            session.save()
            msg = f"Succesfully opened dataset"
            update_dataset_session(session, [msg])
            logger.info(msg)
    except:
        msg = f"Failed to open session: {traceback.format_exc()}."
        logger.error(msg)


@app.task()
def save_dataset_session(id: str, only_modified: bool):
    try:
        session = DatasetSession.objects.get(guid=id)

        msg = f"Saving dataset session {session.guid} on {session.agent.name}"
        update_dataset_session(session, [msg])
        logger.info(msg)

        ssh = SSH(session.agent.hostname, session.agent.port, session.agent.username)

        with ssh:
            msg = f"Transferring {'modified' if only_modified else 'all'} files from {session.agent.name} to {session.path}"
            update_dataset_session(session, [msg])
            logger.info(msg)

            command = f"plantit terrain push {session.path} --terrain_token {session.user.profile.cyverse_token}"
            for file in session.modified:
                command += f" --include_name {file}"

            lines = execute_command(
                ssh_client=ssh,
                pre_command=session.agent.pre_commands,
                command=command,
                directory=session.workdir,
                allow_stderr=True)
            update_dataset_session(session, lines)
    except:
        msg = f"Failed to open session: {traceback.format_exc()}."
        logger.error(msg)


@app.task()
def close_dataset_session(id: str):
    pass


@app.task()
def list_run_results(id: str):
    try:
        run = Run.objects.get(guid=id)
    except:
        logger.info(f"Could not find run {id} (might have been deleted?)")
        return

    redis = RedisClient.get()
    ssh = SSH(run.agent.hostname, run.agent.port, run.agent.username)
    previews = PreviewManager(join(settings.MEDIA_ROOT, run.guid), create_folder=True)
    workflow = redis.get(f"workflow/{run.workflow_owner}/{run.workflow_name}")

    if workflow is None:
        workflow = refresh_workflow(run.workflow_owner, run.workflow_name, run.user.profile.github_token)['config']
    else:
        workflow = json.loads(workflow)['config']

    results = get_run_results(run, workflow)
    workdir = join(run.agent.workdir, run.workdir)
    redis.set(f"results/{run.guid}", json.dumps(results))
    update_run_status(run, f"Found {len(results)} result files")
    print(f"Found {len(results)} result files")

    for res in results:
        name = res['name']
        path = res['path']
        if name.endswith('txt') or \
                name.endswith('csv') or \
                name.endswith('yml') or \
                name.endswith('yaml') or \
                name.endswith('tsv') or \
                name.endswith('out') or \
                name.endswith('err') or \
                name.endswith('log'):
            print(f"Creating preview for text file: {name}")
            with tempfile.NamedTemporaryFile() as temp_file:
                with ssh:
                    with ssh.client.open_sftp() as sftp:
                        sftp.chdir(workdir)
                        sftp.get(name, temp_file.name)

                try:
                    preview = previews.get_jpeg_preview(temp_file.name, width=1024, height=1024)
                except UnsupportedMimeType:
                    redis.set(f"preview/{run.guid}/{name}", 'EMPTY')
                    print(f"Saved empty file preview to cache: {name}")
                    continue

                with open(preview, 'rb') as pf:
                    content = pf.read()
                    encoded = base64.b64encode(content)
                    redis.set(f"preview/{run.guid}/{name}", encoded)
                    print(f"Saved file preview to cache: {name}")
        elif path.endswith('png'):
            print(f"Creating preview for PNG file: {name}")
            with tempfile.NamedTemporaryFile() as temp_file:
                with ssh:
                    with ssh.client.open_sftp() as sftp:
                        sftp.chdir(workdir)
                        sftp.get(res['name'], temp_file.name)

                try:
                    preview = previews.get_jpeg_preview(temp_file.name, width=1024, height=1024)
                except UnsupportedMimeType:
                    redis.set(f"preview/{run.guid}/{name}", 'EMPTY')
                    print(f"Saved empty preview for PNG file to cache: {name}")
                    continue

                with open(preview, 'rb') as pf:
                    content = pf.read()
                    encoded = base64.b64encode(content)
                    redis.set(f"preview/{run.guid}/{name}", encoded)
                    print(f"Saved file preview to cache: {name}")
        elif path.endswith('jpg') or path.endswith('jpeg'):
            print(f"Creating preview for JPG file: {name}")
            with tempfile.NamedTemporaryFile() as temp_file:
                with ssh:
                    with ssh.client.open_sftp() as sftp:
                        sftp.chdir(workdir)
                        sftp.get(res['name'], temp_file.name)

                try:
                    preview = previews.get_jpeg_preview(temp_file.name, width=1024, height=1024)
                except UnsupportedMimeType:
                    redis.set(f"preview/{run.guid}/{name}", 'EMPTY')
                    print(f"Saved empty preview for JPG file to cache: {name}")
                    continue

                with open(preview, 'rb') as pf:
                    content = pf.read()
                    encoded = base64.b64encode(content)
                    redis.set(f"preview/{run.guid}/{name}", encoded)
                    print(f"Saved JPG file preview to cache: {name}")
        elif path.endswith('czi'):
            print(f"Creating preview for CZI file: {name}")
            with tempfile.NamedTemporaryFile() as temp_file:

                with ssh:
                    with ssh.client.open_sftp() as sftp:
                        sftp.chdir(workdir)
                        sftp.get(res['name'], temp_file.name)

                image = czifile.imread(temp_file.name)
                image.shape = (image.shape[2], image.shape[3], image.shape[4])
                success, buffer = cv2.imencode(".jpg", image)
                buffer.tofile(temp_file.name)

                try:
                    preview = previews.get_jpeg_preview(temp_file.name, width=1024, height=1024)
                except UnsupportedMimeType:
                    redis.set(f"preview/{run.guid}/{name}", 'EMPTY')
                    print(f"Saved empty preview for CZI file to cache: {name}")
                    continue

                with open(preview, 'rb') as pf:
                    content = pf.read()
                    encoded = base64.b64encode(content)
                    redis.set(f"preview/{run.guid}/{name}", encoded)
                    print(f"Saved file preview to cache: {name}")
        elif path.endswith('ply'):
            print(f"Creating preview for PLY file: {name}")
            with tempfile.NamedTemporaryFile() as temp_file:
                with ssh:
                    with ssh.client.open_sftp() as sftp:
                        sftp.chdir(workdir)
                        sftp.get(res['name'], temp_file.name)

    run.previews_loaded = True
    run.save()

    update_run_status(run, f"Created file previews")


@app.task()
def aggregate_usage_statistics(username: str):
    try:
        user = User.objects.get(username=username)
    except:
        logger.info(f"Could not find user {username}")
        return

    redis = RedisClient.get()
    logger.info(f"Aggregating usage statistics for {username}")

    completed_runs = list(Run.objects.filter(user__exact=user, completed__isnull=False))
    total_runs = Run.objects.filter(user__exact=user).count()
    total_time = sum([(run.completed - run.created) for run in completed_runs])
    total_results = sum([len(run.results) for run in completed_runs])
    redis.set(f"stats/{username}", json.dumps({
        'total_runs': total_runs,
        'total_time': total_time,
        'total_results': total_results
    }))

    user.profile.stats_last_aggregated = timezone.now()
    user.profile.save()

    # async_to_sync(get_channel_layer().group_send)(f"users-{user.username}", {
    #     'type': 'update_run_status',
    #     'run': map_user(user),
    # })
