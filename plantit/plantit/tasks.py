import base64
import fileinput
import json
import sys
import tempfile
import traceback
from os import environ
from os.path import join

import cv2
from asgiref.sync import async_to_sync
from celery.utils.log import get_task_logger
from channels.layers import get_channel_layer
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
from plantit.submissions.models import Submission, SubmissionStatus
from plantit.submissions.utils import update_submission_status, remove_logs, create_submission, \
    get_container_log_file_name, get_container_log_file_path, get_result_files, get_job_walltime, get_job_status, submit_via_ssh, \
    upload_submission
from plantit.ssh import SSH, execute_command
from plantit.terrain import list_dir
from plantit.sns import SnsClient
from plantit.github import get_repo
from plantit.workflows.models import Workflow

logger = get_task_logger(__name__)


@app.task(track_started=True)
def create_and_submit_workflow(username: str, agent_name: str, workflow: dict):
    submission = create_submission(username, agent_name, workflow)
    submit_workflow.s(submission.guid, workflow).apply_async()


@app.task(track_started=True)
def submit_workflow(guid: str, workflow):
    try:
        submission = Submission.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find run {guid} (might have been deleted?)")
        return

    submission.job_status = 'RUNNING'
    submission.celery_task_id = submit_workflow.request.id  # set the Celery task's ID so user can cancel
    submission.save()

    msg = f"Deploying run {submission.guid} to {submission.agent.name}"
    update_submission_status(submission, msg)
    logger.info(msg)

    try:
        if 'auth' in workflow:
            msg = f"Authenticating with username {workflow['auth']['username']}"
            update_submission_status(submission, msg)
            logger.info(msg)
            ssh_client = SSH(submission.agent.hostname, submission.agent.port, workflow['auth']['username'], workflow['auth']['password'])
        else:
            ssh_client = SSH(submission.agent.hostname, submission.agent.port, submission.agent.username)

        with ssh_client:
            if 'input' in workflow['config'] and workflow['config']['input']['kind'] == 'files':
                input_files = list_dir(workflow['config']['input']['from'], submission.user.profile.cyverse_token)
                msg = f"Found {len(input_files)} input files"
                update_submission_status(submission, msg)
                logger.info(msg)
            else:
                input_files = None

            msg = f"Creating working directory {join(submission.agent.workdir, submission.guid)} and uploading workflow configuration"
            update_submission_status(submission, msg)
            logger.info(msg)
            upload_submission(workflow, submission, ssh_client, input_files)

            msg = 'Running script' if submission.is_sandbox else 'Submitting script to scheduler'
            update_submission_status(submission, msg)
            logger.info(msg)
            submit_via_ssh(submission, ssh_client, len(input_files) if input_files is not None else None)

            if submission.is_sandbox:
                submission.status = SubmissionStatus.SUCCESS
                now = timezone.now()
                submission.updated = now
                submission.completed = now
                submission.save()
                list_submission_results.s(guid).apply_async()

                cleanup_delay = int(environ.get('RUNS_CLEANUP_MINUTES'))
                msg = f"Completed run {submission.guid}, cleaning up in {cleanup_delay}m"
                update_submission_status(submission, msg)
                logger.info(msg)
                cleanup_submission.s(guid).apply_async(countdown=cleanup_delay * 60)

                if submission.user.profile.push_notification_status == 'enabled':
                    SnsClient.get().publish_message(submission.user.profile.push_notification_topic_arn, f"PlantIT run {submission.guid}", msg, {})
            else:
                delay = int(environ.get('RUNS_REFRESH_SECONDS'))
                poll_submission_status.s(submission.guid).apply_async(countdown=delay)
    except Exception:
        submission.status = SubmissionStatus.FAILURE
        now = timezone.now()
        submission.updated = now
        submission.completed = now
        submission.save()

        msg = f"Failed to submit run {submission.guid}: {traceback.format_exc()}."
        update_submission_status(submission, msg)
        logger.error(msg)


@app.task()
def poll_submission_status(guid: str):
    try:
        submission = Submission.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find submission {guid} (might have been deleted?)")
        return

    refresh_delay = int(environ.get('RUNS_REFRESH_SECONDS'))
    cleanup_delay = int(environ.get('RUNS_CLEANUP_MINUTES')) * 60
    logger.info(f"Checking {submission.agent.name} scheduler status for run {guid} (SLURM job {submission.job_id})")

    # if the job already failed, schedule cleanup
    if submission.job_status == 'FAILURE':
        submission.status = SubmissionStatus.FAILURE
        msg = f"Job {submission.job_id} failed, cleaning up in {cleanup_delay}m"
        update_submission_status(submission, msg)
        cleanup_submission.s(guid).apply_async(countdown=cleanup_delay)

        if submission.user.profile.push_notification_status == 'enabled':
            SnsClient.get().publish_message(submission.user.profile.push_notification_topic_arn, f"PlantIT run {submission.guid}", msg, {})

    # otherwise poll the scheduler for its status
    try:
        job_status = get_job_status(submission)
        job_walltime = get_job_walltime(submission)
        submission.job_status = job_status
        submission.job_elapsed_walltime = job_walltime

        now = timezone.now()
        submission.updated = now
        submission.save()

        # get container logs
        work_dir = join(submission.agent.workdir, submission.workdir)
        ssh_client = SSH(submission.agent.hostname, submission.agent.port, submission.agent.username)
        container_log_file = get_container_log_file_name(submission)
        container_log_path = get_container_log_file_path(submission)

        with ssh_client:
            with ssh_client.client.open_sftp() as sftp:
                cmd = 'test -e {0} && echo exists'.format(join(work_dir, container_log_file))
                stdin, stdout, stderr = ssh_client.client.exec_command(cmd)

                if not stdout.read().decode().strip() == 'exists':
                    container_logs = []
                else:
                    with open(get_container_log_file_path(submission), 'a+') as log_file:
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
            submission.completed = now
            submission.status = SubmissionStatus.SUCCESS
        elif job_status == 'FAILED':
            submission.completed = now
            submission.status = SubmissionStatus.FAILURE
        elif job_status == 'CANCELLED':
            submission.completed = now
            submission.status = SubmissionStatus.CANCELED
        elif job_status == 'TIMEOUT':
            submission.completed = now
            submission.status = SubmissionStatus.TIMEOUT

        submission.save()
        if submission.is_complete:
            list_submission_results.s(guid).apply_async()

            msg = f"{submission.agent.executor} job {submission.job_id} {job_status}" + (
                f" after {job_walltime}" if job_walltime is not None else '') + f", cleaning up in {int(environ.get('RUNS_CLEANUP_MINUTES'))}m"
            update_submission_status(submission, msg)
            cleanup_submission.s(guid).apply_async(countdown=cleanup_delay)

            if submission.user.profile.push_notification_status == 'enabled':
                SnsClient.get().publish_message(submission.user.profile.push_notification_topic_arn, f"PlantIT run {submission.guid}", msg, {})
        else:
            msg = f"Job {submission.job_id} {job_status}, walltime {job_walltime}, polling again in {refresh_delay}s"
            update_submission_status(submission, msg)
            poll_submission_status.s(guid).apply_async(countdown=refresh_delay)
    except StopIteration:
        if not (submission.job_status == 'COMPLETED' or submission.job_status == 'COMPLETING'):
            submission.status = SubmissionStatus.FAILURE
            now = timezone.now()
            submission.updated = now
            submission.completed = now
            submission.save()

            msg = f"Job {submission.job_id} not found, cleaning up in {int(environ.get('RUNS_CLEANUP_MINUTES'))}m"
            update_submission_status(submission, msg)
        else:
            msg = f"Job {submission.job_id} succeeded, cleaning up in {int(environ.get('RUNS_CLEANUP_MINUTES'))}m"
            update_submission_status(submission, msg)
            cleanup_submission.s(guid).apply_async(countdown=cleanup_delay)

            if submission.user.profile.push_notification_status == 'enabled':
                SnsClient.get().publish_message(submission.user.profile.push_notification_topic_arn, f"PlantIT run {submission.guid}", msg, {})
    except:
        submission.status = SubmissionStatus.FAILURE
        now = timezone.now()
        submission.updated = now
        submission.completed = now
        submission.save()

        msg = f"Job {submission.job_id} encountered unexpected error (cleaning up in {int(environ.get('RUNS_CLEANUP_MINUTES'))}m): {traceback.format_exc()}"
        update_submission_status(submission, msg)
        cleanup_submission.s(guid).apply_async(countdown=cleanup_delay)

        if submission.user.profile.push_notification_status == 'enabled':
            SnsClient.get().publish_message(submission.user.profile.push_notification_topic_arn, f"PlantIT run {submission.guid}", msg, {})


@app.task()
def cleanup_submission(guid: str):
    try:
        submission = Submission.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find submission {guid} (might have been deleted?)")
        return

    logger.info(f"Cleaning up submission {guid} local working directory {submission.agent.workdir}")
    remove_logs(submission.guid, submission.agent.name)
    logger.info(f"Cleaning up submission {guid} remote working directory {submission.agent.workdir}")
    ssh = SSH(submission.agent.hostname, submission.agent.port, submission.agent.username)
    with ssh:
        execute_command(
            ssh_client=ssh,
            pre_command=submission.agent.pre_commands,
            command=f"rm -r {join(submission.agent.workdir, submission.workdir)}",
            directory=submission.agent.workdir,
            allow_stderr=True)

    submission.cleaned_up = True
    submission.save()

    msg = f"Cleaned up submission {submission.guid}"
    update_submission_status(submission, msg)


@app.task()
def list_submission_results(guid: str):
    try:
        submission = Submission.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find submission {guid} (might have been deleted?)")
        return

    redis = RedisClient.get()
    ssh = SSH(submission.agent.hostname, submission.agent.port, submission.agent.username)
    previews = PreviewManager(join(settings.MEDIA_ROOT, submission.guid), create_folder=True)
    workflow = redis.get(f"workflows/{submission.workflow_owner}/{submission.workflow_name}")

    if workflow is None:
        workflow = get_repo(submission.workflow_owner, submission.workflow_name, submission.user.profile.github_token)['config']
    else:
        workflow = json.loads(workflow)['config']

    results = get_result_files(submission, workflow)
    workdir = join(submission.agent.workdir, submission.workdir)
    redis.set(f"results/{submission.guid}", json.dumps(results))
    update_submission_status(submission, f"Found {len(results)} result files")
    print(f"Found {len(results)} result files")

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
            print(f"Creating preview for text file: {name}")
            with tempfile.NamedTemporaryFile() as temp_file:
                with ssh:
                    with ssh.client.open_sftp() as sftp:
                        sftp.chdir(workdir)
                        sftp.get(name, temp_file.name)

                try:
                    preview = previews.get_jpeg_preview(temp_file.name, width=1024, height=1024)
                except UnsupportedMimeType:
                    redis.set(f"previews/{submission.user.username}/{submission.guid}/{name}", 'EMPTY')
                    print(f"Saved empty file preview to cache: {name}")
                    continue

                with open(preview, 'rb') as pf:
                    content = pf.read()
                    encoded = base64.b64encode(content)
                    redis.set(f"previews/{submission.user.username}/{submission.guid}/{name}", encoded)
                    print(f"Saved file preview to cache: {name}")
        elif path.endswith('png'):
            print(f"Creating preview for PNG file: {name}")
            with tempfile.NamedTemporaryFile() as temp_file:
                with ssh:
                    with ssh.client.open_sftp() as sftp:
                        sftp.chdir(workdir)
                        sftp.get(result['name'], temp_file.name)

                try:
                    preview = previews.get_jpeg_preview(temp_file.name, width=1024, height=1024)
                except UnsupportedMimeType:
                    redis.set(f"previews/{submission.user.username}/{submission.guid}/{name}", 'EMPTY')
                    print(f"Saved empty preview for PNG file to cache: {name}")
                    continue

                with open(preview, 'rb') as pf:
                    content = pf.read()
                    encoded = base64.b64encode(content)
                    redis.set(f"previews/{submission.user.username}/{submission.guid}/{name}", encoded)
                    print(f"Saved file preview to cache: {name}")
        elif path.endswith('jpg') or path.endswith('jpeg'):
            print(f"Creating preview for JPG file: {name}")
            with tempfile.NamedTemporaryFile() as temp_file:
                with ssh:
                    with ssh.client.open_sftp() as sftp:
                        sftp.chdir(workdir)
                        sftp.get(result['name'], temp_file.name)

                try:
                    preview = previews.get_jpeg_preview(temp_file.name, width=1024, height=1024)
                except UnsupportedMimeType:
                    redis.set(f"previews/{submission.user.username}/{submission.guid}/{name}", 'EMPTY')
                    print(f"Saved empty preview for JPG file to cache: {name}")
                    continue

                with open(preview, 'rb') as pf:
                    content = pf.read()
                    encoded = base64.b64encode(content)
                    redis.set(f"previews/{submission.user.username}/{submission.guid}/{name}", encoded)
                    print(f"Saved JPG file preview to cache: {name}")
        elif path.endswith('czi'):
            print(f"Creating preview for CZI file: {name}")
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
                    redis.set(f"previews/{submission.user.username}/{submission.guid}/{name}", 'EMPTY')
                    print(f"Saved empty preview for CZI file to cache: {name}")
                    continue

                with open(preview, 'rb') as pf:
                    content = pf.read()
                    encoded = base64.b64encode(content)
                    redis.set(f"previews/{submission.user.username}/{submission.guid}/{name}", encoded)
                    print(f"Saved file preview to cache: {name}")
        elif path.endswith('ply'):
            print(f"Creating preview for PLY file: {name}")
            with tempfile.NamedTemporaryFile() as temp_file:
                with ssh:
                    with ssh.client.open_sftp() as sftp:
                        sftp.chdir(workdir)
                        sftp.get(result['name'], temp_file.name)

    submission.previews_loaded = True
    submission.save()

    update_submission_status(submission, f"Created file previews")


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

    completed_runs = list(Submission.objects.filter(user__exact=user, completed__isnull=False))
    total_runs = Submission.objects.filter(user__exact=user).count()
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
    #     'type': 'update_status',
    #     'run': map_user(user),
    # })


@app.task()
def refresh_personal_workflows(owner: str):
    try:
        user = User.objects.get(profile__github_username=owner)
    except:
        logger.warning(f"User {owner} does not exist")
        return

    redis = RedisClient.get()
    deleted = 0
    for key in redis.scan_iter(match=f"workflows/{owner}/*"):
        repo = json.loads(redis.get(key))
        deleted += 1
        redis.delete(key)
        async_to_sync(get_channel_layer().group_send)(f"workflows-{owner}", {
            'type': 'remove_workflow',
            'workflow': repo
        })

    logger.info(f"Cleaned {deleted} stale workflow(s) from {owner}'s cache ")

    workflows = Workflow.objects.filter(user=user)
    for workflow in workflows:
        repo = get_repo(workflow.repo_owner, workflow.repo_name, user.profile.github_token)
        repo['public'] = workflow.public
        redis.set(f"workflows/{owner}/{workflow.repo_name}", json.dumps(repo))
        async_to_sync(get_channel_layer().group_send)(f"workflows-{owner}", {
            'type': 'update_workflow',
            'workflow': repo
        })

    logger.info(f"Wrote {len(workflows)} workflow(s) to {owner}'s cache")


@app.task()
def refresh_all_workflows(token: str):
    redis = RedisClient.get()
    public = Workflow.objects.filter(public=True)
    private = Workflow.objects.filter(public=False)

    for workflow in public:
        repo = get_repo(workflow.repo_owner, workflow.repo_name, token)
        repo['public'] = True
        redis.set(f"workflows/{workflow.repo_owner}/{workflow.repo_name}", json.dumps(repo))

    for workflow in private:
        repo = get_repo(workflow.repo_owner, workflow.repo_name, token)
        repo['public'] = False
        redis.set(f"workflows/{workflow.repo_owner}/{workflow.repo_name}", json.dumps(repo))

    logger.info(f"Refreshed public workflows ({len(public)})")
    redis.set(f"public_workflows_updated", timezone.now().timestamp())
