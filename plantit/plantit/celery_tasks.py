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
from plantit.tasks.models import Task, TaskStatus
from plantit.tasks.utils import log_task_status, push_task_event, remove_logs, create_task, \
    get_container_log_file_name, get_container_log_file_path, get_result_files, get_job_walltime, get_job_status, submit_via_ssh, \
    upload_task
from plantit.ssh import SSH, execute_command
from plantit.terrain import list_dir
from plantit.sns import SnsClient
from plantit.github import get_repo
from plantit.workflows.models import Workflow
from plantit.workflows.utils import repopulate_personal_workflow_cache, repopulate_public_workflow_cache

logger = get_task_logger(__name__)


@app.task(track_started=True)
def create_and_submit_task(username: str, agent_name: str, workflow: dict):
    task = create_task(username, agent_name, workflow)
    submit_task.s(task.guid, workflow).apply_async()


@app.task(track_started=True)
def submit_task(guid: str, workflow):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        return

    task.status = TaskStatus.RUNNING
    task.celery_task_id = submit_task.request.id  # set the Celery task's ID so user can cancel
    task.save()

    msg = f"Deploying {task.user.username}'s task {task.name} with GUID {task.guid} to {task.agent.name}"
    log_task_status(task, msg)
    push_task_event(task)
    logger.info(msg)

    try:
        if 'auth' in workflow:
            msg = f"Authenticating with username {workflow['auth']['username']}"
            log_task_status(task, msg)
            push_task_event(task)
            logger.info(msg)
            ssh_client = SSH(task.agent.hostname, task.agent.port, workflow['auth']['username'], workflow['auth']['password'])
        else:
            ssh_client = SSH(task.agent.hostname, task.agent.port, task.agent.username)

        with ssh_client:
            if 'input' in workflow['config'] and workflow['config']['input']['kind'] == 'files':
                input_files = list_dir(workflow['config']['input']['from'], task.user.profile.cyverse_token)
                msg = f"Found {len(input_files)} input files"
                log_task_status(task, msg)
                push_task_event(task)
                logger.info(msg)
            else:
                input_files = None

            msg = f"Creating working directory {join(task.agent.workdir, task.guid)} and uploading files"
            log_task_status(task, msg)
            push_task_event(task)
            logger.info(msg)
            upload_task(workflow, task, ssh_client, input_files)

            msg = 'Running script' if task.is_sandbox else 'Submitting script to scheduler'
            log_task_status(task, msg)
            push_task_event(task)
            logger.info(msg)
            submit_via_ssh(task, ssh_client, len(input_files) if input_files is not None else None)

            if task.is_sandbox:
                task.status = TaskStatus.SUCCESS
                now = timezone.now()
                task.updated = now
                task.completed = now
                task.save()
                list_task_results.s(guid).apply_async()

                cleanup_delay = int(environ.get('RUNS_CLEANUP_MINUTES'))
                msg = f"Completed task with GUID {task.guid}, cleaning up in {cleanup_delay}m"
                log_task_status(task, msg)
                push_task_event(task)
                logger.info(msg)
                cleanup_task.s(guid).apply_async(countdown=cleanup_delay * 60)

                if task.user.profile.push_notification_status == 'enabled':
                    SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT run {task.guid}", msg, {})
            else:
                delay = int(environ.get('RUNS_REFRESH_SECONDS'))
                poll_job_status.s(task.guid).apply_async(countdown=delay)
    except Exception:
        task.status = TaskStatus.FAILURE
        now = timezone.now()
        task.updated = now
        task.completed = now
        task.save()

        msg = f"Failed to submit task with GUID {task.guid}: {traceback.format_exc()}."
        log_task_status(task, msg)
        push_task_event(task)
        logger.error(msg)


@app.task()
def poll_job_status(guid: str):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        return

    refresh_delay = int(environ.get('RUNS_REFRESH_SECONDS'))
    cleanup_delay = int(environ.get('RUNS_CLEANUP_MINUTES')) * 60
    logger.info(f"Checking {task.agent.name} scheduler status for run {guid} (SLURM job {task.job_id})")

    # if the job already failed, schedule cleanup
    if task.job_status == 'FAILURE':
        task.status = TaskStatus.FAILURE
        msg = f"Job {task.job_id} failed, cleaning up in {cleanup_delay}m"
        log_task_status(task, msg)
        push_task_event(task)
        cleanup_task.s(guid).apply_async(countdown=cleanup_delay)

        if task.user.profile.push_notification_status == 'enabled':
            SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT run {task.guid}", msg, {})

    # otherwise poll the scheduler for its status
    try:
        job_status = get_job_status(task)
        job_walltime = get_job_walltime(task)
        task.job_status = job_status
        task.job_elapsed_walltime = job_walltime

        now = timezone.now()
        task.updated = now
        task.save()

        # get container logs
        work_dir = join(task.agent.workdir, task.workdir)
        ssh_client = SSH(task.agent.hostname, task.agent.port, task.agent.username)
        container_log_file = get_container_log_file_name(task)
        container_log_path = get_container_log_file_path(task)

        with ssh_client:
            with ssh_client.client.open_sftp() as sftp:
                cmd = 'test -e {0} && echo exists'.format(join(work_dir, container_log_file))
                stdin, stdout, stderr = ssh_client.client.exec_command(cmd)

                if not stdout.read().decode().strip() == 'exists':
                    container_logs = []
                else:
                    with open(get_container_log_file_path(task), 'a+') as log_file:
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

        if job_status == 'COMPLETED':
            task.completed = now
            task.status = TaskStatus.SUCCESS
        elif job_status == 'FAILED':
            task.completed = now
            task.status = TaskStatus.FAILURE
        elif job_status == 'CANCELLED':
            task.completed = now
            task.status = TaskStatus.CANCELED
        elif job_status == 'TIMEOUT':
            task.completed = now
            task.status = TaskStatus.TIMEOUT

        task.save()
        if task.is_complete:
            list_task_results.s(guid).apply_async()

            msg = f"{task.agent.executor} job {task.job_id} {job_status}" + (
                f" after {job_walltime}" if job_walltime is not None else '') + f", cleaning up in {int(environ.get('RUNS_CLEANUP_MINUTES'))}m"
            log_task_status(task, msg)
            push_task_event(task)
            cleanup_task.s(guid).apply_async(countdown=cleanup_delay)

            if task.user.profile.push_notification_status == 'enabled':
                SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT run {task.guid}", msg, {})
        else:
            msg = f"Job {task.job_id} {job_status}, walltime {job_walltime}, polling again in {refresh_delay}s"
            log_task_status(task, msg)
            push_task_event(task)
            poll_job_status.s(guid).apply_async(countdown=refresh_delay)
    except StopIteration:
        if not (task.job_status == 'COMPLETED' or task.job_status == 'COMPLETING'):
            task.status = TaskStatus.FAILURE
            now = timezone.now()
            task.updated = now
            task.completed = now
            task.save()

            msg = f"Job {task.job_id} not found, cleaning up in {int(environ.get('RUNS_CLEANUP_MINUTES'))}m"
            log_task_status(task, msg)
            push_task_event(task)
        else:
            msg = f"Job {task.job_id} succeeded, cleaning up in {int(environ.get('RUNS_CLEANUP_MINUTES'))}m"
            log_task_status(task, msg)
            push_task_event(task)
            cleanup_task.s(guid).apply_async(countdown=cleanup_delay)

            if task.user.profile.push_notification_status == 'enabled':
                SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT run {task.guid}", msg, {})
    except:
        task.status = TaskStatus.FAILURE
        now = timezone.now()
        task.updated = now
        task.completed = now
        task.save()

        msg = f"Job {task.job_id} encountered unexpected error (cleaning up in {int(environ.get('RUNS_CLEANUP_MINUTES'))}m): {traceback.format_exc()}"
        log_task_status(task, msg)
        push_task_event(task)
        cleanup_task.s(guid).apply_async(countdown=cleanup_delay)

        if task.user.profile.push_notification_status == 'enabled':
            SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT run {task.guid}", msg, {})


@app.task()
def cleanup_task(guid: str):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        return

    logger.info(f"Cleaning up task with GUID {guid} local working directory {task.agent.workdir}")
    remove_logs(task.guid, task.agent.name)
    logger.info(f"Cleaning up task with GUID {guid} remote working directory {task.agent.workdir}")
    ssh = SSH(task.agent.hostname, task.agent.port, task.agent.username)
    with ssh:
        execute_command(
            ssh_client=ssh,
            pre_command=task.agent.pre_commands,
            command=f"rm -r {join(task.agent.workdir, task.workdir)}",
            directory=task.agent.workdir,
            allow_stderr=True)

    task.cleaned_up = True
    task.save()

    msg = f"Cleaned up task {task.guid}"
    log_task_status(task, msg)
    push_task_event(task)


@app.task()
def list_task_results(guid: str):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        return

    redis = RedisClient.get()
    ssh = SSH(task.agent.hostname, task.agent.port, task.agent.username)
    previews = PreviewManager(join(settings.MEDIA_ROOT, task.guid), create_folder=True)
    workflow = redis.get(f"workflows/{task.workflow_owner}/{task.workflow_name}")

    if workflow is None:
        workflow = get_repo(task.workflow_owner, task.workflow_name, task.user.profile.github_token)['config']
    else:
        workflow = json.loads(workflow)['config']

    results = get_result_files(task, workflow)
    workdir = join(task.agent.workdir, task.workdir)
    redis.set(f"results/{task.guid}", json.dumps(results))

    msg = f"Found {len(results)} result files"
    logger.info(msg)
    log_task_status(task, msg)
    push_task_event(task)

    for result in results:
        name = result['name']
        path = result['path']
        if name.endswith('txt') or \
                name.endswith('csv') or \
                name.endswith('yml') or \
                name.endswith('yaml') or \
                name.endswith('tsv') or \
                name.endswith('out') or \
                name.endswith('err') or \
                name.endswith('log'):
            logger.info(f"Creating preview for text file: {name}")
            with tempfile.NamedTemporaryFile() as temp_file:
                with ssh:
                    with ssh.client.open_sftp() as sftp:
                        sftp.chdir(workdir)
                        sftp.get(name, temp_file.name)

                try:
                    preview = previews.get_jpeg_preview(temp_file.name, width=1024, height=1024)
                except UnsupportedMimeType:
                    redis.set(f"previews/{task.user.username}/{task.guid}/{name}", 'EMPTY')
                    logger.info(f"Saved empty file preview to cache: {name}")
                    continue

                with open(preview, 'rb') as pf:
                    content = pf.read()
                    encoded = base64.b64encode(content)
                    redis.set(f"previews/{task.user.username}/{task.guid}/{name}", encoded)
                    logger.info(f"Saved file preview to cache: {name}")
        elif path.endswith('png'):
            logger.info(f"Creating preview for PNG file: {name}")
            with tempfile.NamedTemporaryFile() as temp_file:
                with ssh:
                    with ssh.client.open_sftp() as sftp:
                        sftp.chdir(workdir)
                        sftp.get(result['name'], temp_file.name)

                try:
                    preview = previews.get_jpeg_preview(temp_file.name, width=1024, height=1024)
                except UnsupportedMimeType:
                    redis.set(f"previews/{task.user.username}/{task.guid}/{name}", 'EMPTY')
                    logger.info(f"Saved empty preview for PNG file to cache: {name}")
                    continue

                with open(preview, 'rb') as pf:
                    content = pf.read()
                    encoded = base64.b64encode(content)
                    redis.set(f"previews/{task.user.username}/{task.guid}/{name}", encoded)
                    logger.info(f"Saved file preview to cache: {name}")
        elif path.endswith('jpg') or path.endswith('jpeg'):
            logger.info(f"Creating preview for JPG file: {name}")
            with tempfile.NamedTemporaryFile() as temp_file:
                with ssh:
                    with ssh.client.open_sftp() as sftp:
                        sftp.chdir(workdir)
                        sftp.get(result['name'], temp_file.name)

                try:
                    preview = previews.get_jpeg_preview(temp_file.name, width=1024, height=1024)
                except UnsupportedMimeType:
                    redis.set(f"previews/{task.user.username}/{task.guid}/{name}", 'EMPTY')
                    logger.info(f"Saved empty preview for JPG file to cache: {name}")
                    continue

                with open(preview, 'rb') as pf:
                    content = pf.read()
                    encoded = base64.b64encode(content)
                    redis.set(f"previews/{task.user.username}/{task.guid}/{name}", encoded)
                    logger.info(f"Saved JPG file preview to cache: {name}")
        elif path.endswith('czi'):
            logger.info(f"Creating preview for CZI file: {name}")
            with tempfile.NamedTemporaryFile() as temp_file:

                with ssh:
                    with ssh.client.open_sftp() as sftp:
                        sftp.chdir(workdir)
                        sftp.get(result['name'], temp_file.name)

                image = czifile.imread(temp_file.name)
                image.shape = (image.shape[2], image.shape[3], image.shape[4])
                success, buffer = cv2.imencode(".jpg", image)
                buffer.tofile(temp_file.name)

                try:
                    preview = previews.get_jpeg_preview(temp_file.name, width=1024, height=1024)
                except UnsupportedMimeType:
                    redis.set(f"previews/{task.user.username}/{task.guid}/{name}", 'EMPTY')
                    logger.info(f"Saved empty preview for CZI file to cache: {name}")
                    continue

                with open(preview, 'rb') as pf:
                    content = pf.read()
                    encoded = base64.b64encode(content)
                    redis.set(f"previews/{task.user.username}/{task.guid}/{name}", encoded)
                    logger.info(f"Saved file preview to cache: {name}")
        elif path.endswith('ply'):
            logger.info(f"Creating preview for PLY file: {name}")
            with tempfile.NamedTemporaryFile() as temp_file:
                with ssh:
                    with ssh.client.open_sftp() as sftp:
                        sftp.chdir(workdir)
                        sftp.get(result['name'], temp_file.name)

    task.previews_loaded = True
    task.save()
    log_task_status(task, f"Created file previews")
    push_task_event(task)


@app.task()
def clean_agent_singularity_cache(agent_name: str):
    try:
        agent = Agent.objects.get(name=agent_name)
    except:
        logger.warning(f"Agent {agent_name} does not exist")
        return

    ssh = SSH(agent.hostname, agent.port, agent.username)
    with ssh:
        execute_command(
            ssh_client=ssh,
            pre_command=agent.pre_commands,
            command="singularity cache clean",
            directory=agent.workdir,
            allow_stderr=True)


@app.task()
def execute_agent_command(agent_name: str, command: str, pre_command: str = None):
    try:
        agent = Agent.objects.get(name=agent_name)
    except:
        logger.warning(f"Agent {agent_name} does not exist")
        return

    ssh = SSH(agent.hostname, agent.port, agent.username)
    with ssh:
        lines = execute_command(
            ssh_client=ssh,
            pre_command=agent.pre_commands + '' if pre_command is None else f"&& {pre_command}",
            command=command,
            directory=agent.workdir,
            allow_stderr=True)


@app.task()
def open_dataset_session(guid: str):
    try:
        session = DatasetSession.objects.get(guid=guid)
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
def save_dataset_session(guid: str, only_modified: bool):
    try:
        session = DatasetSession.objects.get(guid=guid)

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
def close_dataset_session(guid: str):
    pass


@app.task()
def aggregate_user_statistics(username: str):
    try:
        user = User.objects.get(owner=username)
    except:
        logger.warning(f"User {username} does not exist")
        return

    redis = RedisClient.get()
    logger.info(f"Aggregating usage statistics for {username}")

    completed_runs = list(Task.objects.filter(user__exact=user, completed__isnull=False))
    total_runs = Task.objects.filter(user__exact=user).count()
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
    #     'type': 'task_event',
    #     'run': map_user(user),
    # })


@app.task()
def refresh_personal_workflows(owner: str):
    repopulate_personal_workflow_cache(owner)


@app.task()
def refresh_all_workflows(token: str):
    repopulate_public_workflow_cache(token)
