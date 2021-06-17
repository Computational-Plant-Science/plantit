import base64
import json
import tempfile
import traceback
from os import environ
from os.path import join

import cv2
from asgiref.sync import async_to_sync
from celery import group
from celery.utils.log import get_task_logger
from czifile import czifile
from django.contrib.auth.models import User
from django.utils import timezone
from preview_generator.exception import UnsupportedMimeType
from preview_generator.manager import PreviewManager

from plantit import settings
from plantit.agents.models import AgentExecutor
from plantit.celery import app
from plantit.github import get_repo
from plantit.redis import RedisClient
from plantit.sns import SnsClient
from plantit.ssh import execute_command
from plantit.tasks.models import Task, TaskStatus
from plantit.utils import log_task_status, push_task_event, get_task_ssh_client, configure_task_environment, execute_local_task, submit_jobqueue_task, \
    get_jobqueue_task_job_status, get_jobqueue_task_job_walltime, get_task_container_logs, remove_task_orchestration_logs, get_task_result_files, \
    repopulate_personal_workflow_cache, repopulate_public_workflow_cache, get_user_statistics

logger = get_task_logger(__name__)


@app.task(track_started=True)
def submit_task(guid: str, auth: dict):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        return

    task.status = TaskStatus.RUNNING
    task.celery_task_id = submit_task.request.id  # set the Celery task's ID so user can cancel
    task.save()

    log_task_status(task, [f"Preparing to submit to {task.agent.name}"])
    async_to_sync(push_task_event)(task)

    try:
        local = task.agent.executor == AgentExecutor.LOCAL
        ssh = get_task_ssh_client(task, auth)

        with ssh:
            log_task_status(task, [f"Configuring environment"])
            async_to_sync(push_task_event)(task)
            configure_task_environment(task, ssh)

            if local:
                log_task_status(task, [f"Invoking script"])
                async_to_sync(push_task_event)(task)

                execute_local_task(task, ssh)
                list_task_results.s(guid, auth).apply_async()
                cleanup_delay = int(environ.get('RUNS_CLEANUP_MINUTES'))
                cleanup_task.s(guid, auth).apply_async(countdown=cleanup_delay * 60)

                final_message = f"Completed, cleaning up in {cleanup_delay} minute(s)"
                log_task_status(task, [final_message])
                async_to_sync(push_task_event)(task)

                if task.user.profile.push_notification_status == 'enabled':
                    SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT task {task.guid}", final_message, {})
            else:
                log_task_status(task, [f"Submitting script"])
                async_to_sync(push_task_event)(task)

                job_id = submit_jobqueue_task(task, ssh)
                refresh_delay = int(environ.get('RUNS_REFRESH_SECONDS'))
                poll_job_status.s(task.guid, auth).apply_async(countdown=refresh_delay)

                log_task_status(task, [f"Scheduled job (ID {job_id}), polling status in {refresh_delay} second(s)"])
                async_to_sync(push_task_event)(task)
    except Exception:
        task.status = TaskStatus.FAILURE
        now = timezone.now()
        task.updated = now
        task.completed = now
        task.save()

        error = traceback.format_exc()
        log_task_status(task, [f"Failed with error: {error}"])
        logger.error(f"Failed to submit {task.user.username}'s task {task.name} to {task.agent.name}: {error}")
        async_to_sync(push_task_event)(task)


@app.task()
def poll_job_status(guid: str, auth: dict):
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
        final_message = f"Job {task.job_id} failed, cleaning up in {cleanup_delay}m"
        log_task_status(task, [final_message])
        async_to_sync(push_task_event)(task)
        cleanup_task.s(guid).apply_async(countdown=cleanup_delay)

        if task.user.profile.push_notification_status == 'enabled':
            SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT task {task.guid}", final_message, {})

    # otherwise poll the scheduler for its status
    try:
        job_status = get_jobqueue_task_job_status(task)
        job_walltime = get_jobqueue_task_job_walltime(task)
        task.job_status = job_status
        task.job_elapsed_walltime = job_walltime

        now = timezone.now()
        task.updated = now
        task.save()

        ssh = get_task_ssh_client(task, auth)
        get_task_container_logs(task, ssh)

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
            final_message = f"{task.agent.executor} job {task.job_id} {job_status}" + (
                f" after {job_walltime}" if job_walltime is not None else '') + f", cleaning up in {int(environ.get('RUNS_CLEANUP_MINUTES'))}m"
            log_task_status(task, [final_message])
            async_to_sync(push_task_event)(task)
            cleanup_task.s(guid).apply_async(countdown=cleanup_delay)

            if task.user.profile.push_notification_status == 'enabled':
                SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT task {task.guid}", final_message, {})
        else:
            log_task_status(task, [f"Job {task.job_id} {job_status}, walltime {job_walltime}, polling again in {refresh_delay}s"])
            async_to_sync(push_task_event)(task)
            poll_job_status.s(guid).apply_async(countdown=refresh_delay)
    except StopIteration:
        if not (task.job_status == 'COMPLETED' or task.job_status == 'COMPLETING'):
            task.status = TaskStatus.FAILURE
            now = timezone.now()
            task.updated = now
            task.completed = now
            task.save()

            log_task_status(task, [f"Job {task.job_id} not found, cleaning up in {int(environ.get('RUNS_CLEANUP_MINUTES'))}m"])
            async_to_sync(push_task_event)(task)
        else:
            final_message = f"Job {task.job_id} succeeded, cleaning up in {int(environ.get('RUNS_CLEANUP_MINUTES'))}m"
            log_task_status(task, [final_message])
            async_to_sync(push_task_event)(task)
            cleanup_task.s(guid).apply_async(countdown=cleanup_delay)

            if task.user.profile.push_notification_status == 'enabled':
                SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT task {task.guid}", final_message, {})
    except:
        task.status = TaskStatus.FAILURE
        now = timezone.now()
        task.updated = now
        task.completed = now
        task.save()

        final_message = f"Job {task.job_id} encountered unexpected error (cleaning up in {int(environ.get('RUNS_CLEANUP_MINUTES'))}m): {traceback.format_exc()}"
        log_task_status(task, [final_message])
        async_to_sync(push_task_event)(task)
        cleanup_task.s(guid).apply_async(countdown=cleanup_delay)

        if task.user.profile.push_notification_status == 'enabled':
            SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT task {task.guid}", final_message, {})


@app.task()
def cleanup_task(guid: str, auth: dict):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        return

    logger.info(f"Cleaning up task with GUID {guid} local working directory {task.agent.workdir}")
    remove_task_orchestration_logs(task.guid)

    logger.info(f"Cleaning up task with GUID {guid} remote working directory {task.agent.workdir}")
    command = f"rm -rf {join(task.agent.workdir, task.workdir)}"
    ssh = get_task_ssh_client(task, auth)
    with ssh:
        for line in execute_command(ssh=ssh, precommand=task.agent.pre_commands, command=command, directory=task.agent.workdir, allow_stderr=True):
            logger.info(f"[{task.agent.name}] {line}")

    task.cleaned_up = True
    task.save()

    log_task_status(task, [f"Cleaned up task {task.guid}"])
    async_to_sync(push_task_event)(task)


@app.task()
def list_task_results(guid: str, auth: dict):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        return

    redis = RedisClient.get()
    ssh = get_task_ssh_client(task, auth)
    previews = PreviewManager(join(settings.MEDIA_ROOT, task.guid), create_folder=True)
    workflow = redis.get(f"workflows/{task.workflow_owner}/{task.workflow_name}")

    if workflow is None:
        workflow = get_repo(task.workflow_owner, task.workflow_name, task.user.profile.github_token)['config']
    else:
        workflow = json.loads(workflow)['config']

    log_task_status(task, [f"Retrieving logs"])
    async_to_sync(push_task_event)(task)

    get_task_container_logs(task, ssh)

    log_task_status(task, [f"Retrieving results"])
    async_to_sync(push_task_event)(task)

    expected = get_task_result_files(task, workflow, auth)
    found = [e for e in expected if e['exists']]
    workdir = join(task.agent.workdir, task.workdir)
    redis.set(f"results/{task.guid}", json.dumps(expected))

    log_task_status(task, [f"Expected {len(expected)} result(s), found {len(found)}"])
    async_to_sync(push_task_event)(task)

    for result in expected:
        name = result['name']
        path = result['path']
        exists = result['exists']

        if not exists: continue
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
    log_task_status(task, [f"Created file previews"])
    async_to_sync(push_task_event)(task)


# @app.task()
# def clean_agent_singularity_cache(agent_name: str):
#     try:
#         agent = Agent.objects.get(name=agent_name)
#     except:
#         logger.warning(f"Agent {agent_name} does not exist")
#         return
#
#     ssh = SSH(agent.hostname, agent.port, agent.username)
#     with ssh:
#         for line in execute_command(
#                 ssh_client=ssh,
#                 pre_command=agent.pre_commands,
#                 command="singularity cache clean",
#                 directory=agent.workdir,
#                 allow_stderr=True):
#             logger.info(line)


# @app.task()
# def execute_agent_command(agent_name: str, command: str, pre_command: str = None):
#     try:
#         agent = Agent.objects.get(name=agent_name)
#     except:
#         logger.warning(f"Agent {agent_name} does not exist")
#         return
#
#     ssh = SSH(agent.hostname, agent.port, agent.username)
#     with ssh:
#         for line in execute_command(
#                 ssh_client=ssh,
#                 pre_command=agent.pre_commands + '' if pre_command is None else f"&& {pre_command}",
#                 command=command,
#                 directory=agent.workdir,
#                 allow_stderr=True):
#             logger.info(line)


# @app.task()
# def open_dataset_session(guid: str):
#     try:
#         session = DatasetSession.objects.get(guid=guid)
#         ssh = SSH(session.agent.hostname, session.agent.port, session.agent.username)
#
#         with ssh:
#             msg = f"Creating working directory {session.workdir}"
#             update_dataset_session(session, [f"Creating working directory {session.workdir}"])
#             logger.info(msg)
#
#             for line in execute_command(
#                     ssh_client=ssh,
#                     pre_command=':',
#                     command=f"mkdir {session.guid}/",
#                     directory=session.agent.workdir):
#                 logger.info(line)
#
#             msg = f"Transferring files from {session.path} to {session.agent.name}"
#             update_dataset_session(session, [msg])
#             logger.info(msg)
#
#             command = f"plantit terrain pull \"{session.path}\" --terrain_token {session.user.profile.cyverse_access_token}\n"
#             for line in execute_command(
#                     ssh_client=ssh,
#                     pre_command=session.agent.pre_commands,
#                     command=command,
#                     directory=session.workdir,
#                     allow_stderr=True):
#                 update_dataset_session(session, [line])
#
#             session.opening = False
#             session.save()
#             msg = f"Succesfully opened dataset"
#             update_dataset_session(session, [msg])
#             logger.info(msg)
#     except:
#         msg = f"Failed to open session: {traceback.format_exc()}."
#         logger.error(msg)


# @app.task()
# def save_dataset_session(guid: str, only_modified: bool):
#     try:
#         session = DatasetSession.objects.get(guid=guid)
#
#         msg = f"Saving dataset session {session.guid} on {session.agent.name}"
#         update_dataset_session(session, [msg])
#         logger.info(msg)
#
#         ssh = SSH(session.agent.hostname, session.agent.port, session.agent.username)
#
#         with ssh:
#             msg = f"Transferring {'modified' if only_modified else 'all'} files from {session.agent.name} to {session.path}"
#             update_dataset_session(session, [msg])
#             logger.info(msg)
#
#             command = f"plantit terrain push {session.path} --terrain_token {session.user.profile.cyverse_access_token}"
#             for file in session.modified:
#                 command += f" --include_name {file}"
#
#             for line in execute_command(
#                     ssh_client=ssh,
#                     pre_command=session.agent.pre_commands,
#                     command=command,
#                     directory=session.workdir,
#                     allow_stderr=True):
#                 update_dataset_session(session, [line])
#     except:
#         msg = f"Failed to open session: {traceback.format_exc()}."
#         logger.error(msg)


# @app.task()
# def close_dataset_session(guid: str):
#     pass


@app.task()
def aggregate_user_statistics():
    users = User.objects.all()
    for user in users:
        logger.info(f"Aggregating usage statistics for {user.username}")
        stats = async_to_sync(get_user_statistics)(user)
        redis = RedisClient.get()
        redis.set(f"stats/{user.username}", json.dumps(stats))
        user.profile.stats_last_aggregated = timezone.now()
        user.profile.save()


@app.task()
def refresh_personal_workflows(owner: str):
    repopulate_personal_workflow_cache(owner)


@app.task()
def refresh_all_workflows(token: str):
    repopulate_public_workflow_cache(token)


@app.task()
def refresh_user_cyverse_tokens(username: str):
    try:
        user = User.objects.get(username=username)
    except:
        logger.warning(f"User {username} not found")
        return

    refresh_user_cyverse_tokens(user)


@app.task()
def refresh_all_user_cyverse_tokens():
    tasks = Task.objects.filter(status=TaskStatus.RUNNING)
    users = [task.user for task in list(tasks)]

    if len(users) == 0:
        logger.info(f"No users with running tasks, not refreshing CyVerse tokens")
        return

    group([refresh_user_cyverse_tokens.s(user.username) for user in users])()
    logger.info(f"Refreshed CyVerse tokens for {len(users)} user(s)")


# see https://stackoverflow.com/a/41119054/6514033
# `@app.on_after_finalize.connect` is necessary for some reason instead of `@app.on_after_configure.connect`
@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    logger.info("Scheduling periodic tasks")

    # refresh CyVerse auth tokens for all users with running tasks (in case outputs need to get pushed on completion)
    sender.add_periodic_task(int(settings.CYVERSE_TOKEN_REFRESH_MINUTES) * 60, refresh_all_user_cyverse_tokens.s(), name='refresh CyVerse tokens')

    # aggregate usage stats for each user
    sender.add_periodic_task(int(settings.USERS_STATS_REFRESH_MINUTES) * 60, aggregate_user_statistics.s(), name='aggregate user statistics')
