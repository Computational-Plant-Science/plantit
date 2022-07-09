import json
import os
import traceback
from copy import deepcopy
from pathlib import Path
from typing import List, NamedTuple, Optional
from os import environ
from os.path import join
from datetime import datetime

from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer
from celery import group
from celery.utils.log import get_task_logger
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils import timezone
from pycyapi.clients import TerrainClient

import plantit.healthchecks
import plantit.mapbox
import plantit.queries as q
import plantit.utils.agents
import plantit.migration as mig
from plantit.ssh import SSH
from plantit.keypairs import get_user_private_key_path
from plantit import settings
from plantit.users.models import Profile, Migration, ManagedFile
from plantit.agents.models import Agent
from plantit.celery import app
from plantit.healthchecks import is_healthy
from plantit.queries import refresh_user_workflow_cache, refresh_online_users_workflow_cache, refresh_online_user_orgs_workflow_cache, \
    refresh_user_cyverse_tokens
from plantit.redis import RedisClient
from plantit.sns import SnsClient
from plantit.ssh import execute_command
from plantit.task_lifecycle import parse_task_options, create_immediate_task, upload_deployment_artifacts, submit_job_to_scheduler, \
    get_job_status_and_walltime, list_result_files, cancel_task, submit_pull_to_scheduler, submit_push_to_scheduler
from plantit.task_resources import get_task_ssh_client, push_task_channel_event, log_task_status
from plantit.tasks.models import Task, TriggeredTask, TaskStatus

logger = get_task_logger(__name__)


@app.task(track_started=True)
def create_and_submit_delayed(username, workflow, delayed_id: str = None):
    try:
        user = User.objects.get(username=username)
    except:
        logger.error(traceback.format_exc())
        return

    # create task
    task = create_immediate_task(user, workflow)
    if delayed_id is not None: task.delayed_id = delayed_id
    task.save()

    # submit head of (task chain to) Celery
    (prep_environment.s(task.guid) | share_data.s() | submit_jobs.s() | poll_jobs.s()).apply_async(
        countdown=5,  # TODO: make initial delay configurable
        soft_time_limit=int(settings.TASKS_STEP_TIME_LIMIT_SECONDS))

    log_task_status(task, [f"Created {task.user.username}'s (delayed) task {task.guid} on {task.agent.name}"])
    async_to_sync(push_task_channel_event)(task)


@app.task(track_started=True)
def create_and_submit_repeating(username, workflow, repeating_id: str = None):
    try:
        user = User.objects.get(username=username)
    except:
        logger.error(traceback.format_exc())
        return

    # create task
    task = create_immediate_task(user, workflow)
    if repeating_id is not None: task.delayed_id = repeating_id
    task.save()

    # submit head of (task chain to) Celery
    (prep_environment.s(task.guid) | share_data.s() | submit_jobs.s() | poll_jobs.s()).apply_async(
        countdown=5,  # TODO: make initial delay configurable
        soft_time_limit=int(settings.TASKS_STEP_TIME_LIMIT_SECONDS))

    log_task_status(task, [f"Created {task.user.username}'s (repeating) task {task.guid} on {task.agent.name}"])
    async_to_sync(push_task_channel_event)(task)


@app.task(track_started=True)
def create_and_submit_triggered(username, workflow, triggered_id: str = None):
    try:
        user = User.objects.get(username=username)
        task = TriggeredTask.objects.get(name=triggered_id)
    except:
        logger.error(traceback.format_exc())
        return

    # check if the data have changed since last time we checked
    client = TerrainClient(access_token=task.user.profile.cyverse_access_token)
    modified = datetime.fromtimestamp(int(str(client.stat(path=task.path)['date-modified']).strip("0")))

    # if the data haven't changed, nothing to do
    if task.modified <= modified:
        logger.info(f"{task.user.username}'s triggered task {triggered_id} for path {task.path} skipped; data haven't changed")
        return
    else:
        # otherwise we need to update the last modified timestamp on the task
        task.modified = modified
        task.save()

    # create task
    itask = create_immediate_task(user, workflow)
    if triggered_id is not None: itask.triggered_id = triggered_id
    task.save()

    # submit head of (task chain to) Celery
    (prep_environment.s(itask.guid) | share_data.s() | submit_jobs.s() | poll_jobs.s()).apply_async(
        countdown=5,  # TODO: make initial delay configurable
        soft_time_limit=int(settings.TASKS_STEP_TIME_LIMIT_SECONDS))

    log_task_status(itask, [f"Created {task.user.username}'s (triggered) task {itask.guid} on {itask.agent.name}"])
    async_to_sync(push_task_channel_event)(itask)


#  Task Lifecycle  #
#
# prep environment
# share dataset
# submit script
# poll status
# (if successful)
#   check results
#   check transfer
# unshare dataset
# clean up


def __handle_job_success(task: Task, message: str):
    # update the task and persist it
    now = timezone.now()
    task.updated = now
    task.job_status = TaskStatus.COMPLETED
    task.save()

    # log status to file and push to client(s)
    log_task_status(task, [message])
    async_to_sync(push_task_channel_event)(task)

    # push AWS SNS task completion notification
    if task.user.profile.push_notification_status == 'enabled':
        SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT task {task.guid}", message, {})

    # submit the outbound data transfer job
    (test_results.s(task.guid) | test_push.s() | unshare_data.s()).apply_async(soft_time_limit=int(settings.TASKS_STEP_TIME_LIMIT_SECONDS))
    tidy_up.s(task.guid).apply_async(countdown=int(environ.get('TASKS_CLEANUP_MINUTES')) * 60)


def __handle_job_failure(task: Task, message: str):
    # mark the task failed and persist it
    task.status = TaskStatus.FAILURE
    now = timezone.now()
    task.updated = now
    task.completed = now
    task.save()

    # log status to file and push to client(s)
    log_task_status(task, [message])
    async_to_sync(push_task_channel_event)(task)

    # push AWS SNS notification
    if task.user.profile.push_notification_status == 'enabled':
        SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT task {task.guid}", message, {})

    # revoke access to the user's datasets then clean up the task
    unshare_data.s(task.guid).apply_async()
    tidy_up.s(task.guid).apply_async(countdown=int(environ.get('TASKS_CLEANUP_MINUTES')) * 60)


@app.task(track_started=True, bind=True)
def prep_environment(self, guid: str):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task {guid} (might have been deleted?)")
        self.request.callbacks = None
        return

    if task.status == TaskStatus.CANCELED:
        logger.warning(f"Task {guid} cancelled, aborting")
        self.request.callbacks = None
        return

    try:
        # check task configuration for errors
        parse_errors, options = parse_task_options(task)
        if len(parse_errors) > 0: raise ValueError(f"Failed to parse task options: {' '.join(parse_errors)}")

        # create working directory and upload deployment artifacts to agent
        work_dir = join(task.agent.workdir, task.guid)
        ssh = get_task_ssh_client(task)
        with ssh:
            for line in list(execute_command(ssh=ssh, setup_command=':', command=f"mkdir -v {work_dir}")): logger.info(line)
            upload_deployment_artifacts(task, ssh, options)

        # set task to running
        task.status = TaskStatus.RUNNING
        task.save()

        log_task_status(task, [f"Prepared environment"])
        async_to_sync(push_task_channel_event)(task)

        return guid
    except Exception:
        self.request.callbacks = None
        __handle_job_failure(task, f"Failed to prep environment: {traceback.format_exc()}")


@app.task(track_started=True, bind=True)
def share_data(self, guid: str):
    if guid is None:
        logger.debug(f"Aborting")
        self.request.callbacks = None
        return

    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task {guid} (might have been deleted?)")
        self.request.callbacks = None
        return

    if task.status == TaskStatus.CANCELED:
        logger.warning(f"Task {guid} cancelled, aborting")
        self.request.callbacks = None
        return

    # if any other running tasks share the same outbound transfer path, we already have access (no need to share)
    # TODO remove after unblocked here: https://github.com/Computational-Plant-Science/plantit/issues/225
    # if Task.objects\
    #         .filter(user=task.user, status__in=[TaskStatus.CREATED, TaskStatus.RUNNING], transfer_path=task.transfer_path)\
    #         .exclude(guid=task.guid)\
    #         .count() != 0:
    #     logger.warning(
    #         f"Task {guid} outbound path {task.transfer_path} used by another task, not granting temporary data access")
    #     self.request.callbacks = None
    #     return guid

    # if the admin user owns this task, we don't need to share/unshare datasets
    if task.user.username == settings.CYVERSE_USERNAME:
        logger.info(f"Admin user {settings.CYVERSE_USERNAME} owns task {guid}, no need to grant temporary data access")
        return guid

    try:
        options = task.workflow
        output_path = options['output']['to']
        paths = [
            {
                'path': output_path,
                'permission': 'write'
            }
        ]
        if 'input' in options:
            input_path = options['input']['path']
            if ('/iplant/home/shared' not in input_path and  # no need for temporary access if input is public shared dir
                    input_path != output_path):  # skip input permissions if reading and writing from same dir
                paths.append({
                    'path': input_path,
                    'permission': 'write'
                })

        # share the user's source and target collections with the plantit CyVerse user
        client = TerrainClient(access_token=task.user.profile.cyverse_access_token)
        client.share_many(username=settings.CYVERSE_USERNAME, paths=paths)

        # log_task_status(task, [f"Granted temporary data access"])
        # async_to_sync(push_task_channel_event)(task)

        return guid
    except Exception:
        logger.warning(traceback.format_exc())
        self.request.callbacks = None
        __handle_job_failure(task, f"Failed to grant temporary data access")


@app.task(track_started=True, bind=True)
def submit_jobs(self, guid: str):
    if guid is None:
        logger.debug(f"Aborting")
        self.request.callbacks = None
        return

    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        self.request.callbacks = None
        return

    if task.status == TaskStatus.CANCELED:
        logger.warning(f"Task {guid} cancelled, aborting")
        self.request.callbacks = None
        return

    try:
        # check task configuration for errors
        parse_errors, options = parse_task_options(task)
        if len(parse_errors) > 0: raise ValueError(f"Failed to parse task options: {' '.join(parse_errors)}")

        ssh = get_task_ssh_client(task)
        with ssh:
            job_ids = []

            # only schedule inbound transfer if we have inputs
            if 'input' in options:
                pull_id = submit_pull_to_scheduler(task, ssh)
                async_to_sync(push_task_channel_event)(task)
                job_ids.append(pull_id + ' (inbound transfer)')
            else:
                pull_id = None

            # schedule user workflow and outbound transfer jobs
            job_id = submit_job_to_scheduler(task, ssh, pull_id=pull_id)
            push_id = submit_push_to_scheduler(task, ssh, job_id=job_id)
            job_ids.extend([job_id + ' (user workflow)', push_id + ' (outbound transfer)'])

            # persist the last job ID to the task
            task.job_id = push_id
            task.updated = timezone.now()
            task.save()
            logger.info(f"Task {task.guid} job ID: {task.job_id}")

            log_task_status(task, [f"Scheduled jobs {', '.join(job_ids)}"])
            async_to_sync(push_task_channel_event)(task)

        return guid
    except Exception:
        self.request.callbacks = None
        __handle_job_failure(task, f"Failed to schedule jobs: {traceback.format_exc()}")


@app.task(track_started=True, bind=True)
def poll_jobs(self, guid: str):
    if guid is None:
        logger.debug(f"Aborting")
        self.request.callbacks = None
        return

    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        self.request.callbacks = None  # stop the task chain
        return

    if task.status == TaskStatus.CANCELED:
        logger.warning(f"Task {guid} cancelled, aborting")
        self.request.callbacks = None
        return

    # poll the scheduler for job status and walltime
    try:
        refresh_delay = int(environ.get('TASKS_REFRESH_SECONDS'))
        logger.info(f"Checking {task.agent.name} scheduler status for task {guid} job {task.job_id}")
        job_status, _ = get_job_status_and_walltime(task)  # returns None if the job isn't found in the agent's scheduler.

        # there are 2 reasons a job might not be found:
        #   - it was just submitted and hasn't been picked up for reporting by the scheduler yet
        #   - it already completed and we waited too long between polls to check its status
        if job_status is None:
            # update the task and persist it
            now = timezone.now()
            task.updated = now
            task.job_status = job_status
            # task.job_consumed_walltime = job_walltime
            task.save()

            # we might have just submitted the job; scheduler may take a moment to reflect new submissions
            if not (task.job_status == 'COMPLETED' or task.job_status == 'COMPLETING'):
                # wait and poll again
                logger.warning(f"Job {task.job_id} not found yet, retrying in {refresh_delay}s")
                poll_jobs.s(guid).apply_async(countdown=refresh_delay)
            else:
                # otherwise the job completed and the scheduler's forgotten about it in the interval between polls
                __handle_job_success(task, f"Job {task.job_id} ended with unknown status")

            # in either case, return early
            return guid

        # if job did not complete, go ahead and mark the task failed/cancelled/timed out/etc
        job_complete = False
        if job_status in Task.SLURM_FAILURE_STATES:
            task.status = TaskStatus.FAILURE
            job_complete = True
        elif job_status in Task.SLURM_CANCELLED_STATES:
            task.status = TaskStatus.CANCELED
            job_complete = True
        elif job_status in task.SLURM_TIMEOUT_STATES:
            task.status = TaskStatus.TIMEOUT
            job_complete = True
        # but if it succeeded, we're not done yet
        elif job_status in task.SLURM_SUCCESS_STATES:
            job_complete = True

        # update the task and persist it
        task.job_status = job_status
        # task.job_consumed_walltime = job_walltime
        now = timezone.now()
        task.updated = now
        task.save()

        if job_complete:
            __handle_job_success(task, f"Job {task.job_id} ended with status {job_status}")
            return guid
        else:
            # if past due time...
            if now > task.due_time:
                cancel_task(task)
                __handle_job_failure(task, f"Job {task.job_id} {job_status} is past its due time {str(task.due_time)} and was cancelled")
            else:
                # log the status update
                # log_task_status(task, [f"Job {task.job_id} {job_status}, refreshing in {refresh_delay}s"])

                # push status to client(s)
                async_to_sync(push_task_channel_event)(task)

                # wait and poll again
                poll_jobs.s(guid).apply_async(countdown=refresh_delay)
    except:
        self.request.callbacks = None
        __handle_job_failure(task, f"Failed to poll job {task.job_id} status: {traceback.format_exc()}")


@app.task(track_started=True, bind=True)
def test_results(self, guid: str):
    if guid is None:
        logger.debug(f"Aborting")
        self.request.callbacks = None
        return

    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        self.request.callbacks = None
        return

    if task.status == TaskStatus.CANCELED:
        logger.warning(f"Task {guid} cancelled, aborting")
        self.request.callbacks = None
        return

    try:
        # get logs from agent filesystem
        # ssh = get_task_ssh_client(task)
        # get_task_remote_logs(task, ssh)

        # get results from agent filesystem, then save them to cache and update the task
        results = list_result_files(task)
        found = [r for r in results if r['exists']]

        redis = RedisClient.get()
        redis.set(f"results/{task.guid}", json.dumps(found))
        task.results_retrieved = True
        task.save()

        # make sure we got the results we expected
        missing = [r for r in results if not r['exists']]
        if len(missing) > 0:
            message = f"Found {len(found)} results, missing {len(missing)}: {', '.join([m['name'] for m in missing])}"
        else:
            message = f"Found {len(found)} results"

        # log status update and push it to client(s)
        log_task_status(task, [message])
        async_to_sync(push_task_channel_event)(task)

        return guid
    except Exception:
        self.request.callbacks = None
        message = f"Failed to check results: {traceback.format_exc()}"

        # mark the task failed and persist it
        task.status = TaskStatus.FAILURE
        now = timezone.now()
        task.updated = now
        task.completed = now
        task.save()

        # log status to file
        log_task_status(task, [message])

        # push status to client(s)
        async_to_sync(push_task_channel_event)(task)

        # push AWS SNS notification
        if task.user.profile.push_notification_status == 'enabled':
            SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT task {task.guid}", message, {})

        # revoke access to the user's datasets then clean up the task
        unshare_data.s(task.guid).apply_async()
        tidy_up.s(task.guid).apply_async(countdown=int(environ.get('TASKS_CLEANUP_MINUTES')) * 60)


@app.task(track_started=True, bind=True)
def test_push(self, guid: str):
    if guid is None:
        logger.debug(f"Aborting")
        self.request.callbacks = None
        return

    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        return

    if task.status == TaskStatus.CANCELED:
        logger.warning(f"Task {guid} cancelled, aborting")
        self.request.callbacks = None
        return

    try:
        # check the expected filenames against the contents of the CyVerse collection
        path = task.workflow['output']['to']

        client = TerrainClient(access_token=task.user.profile.cyverse_access_token)
        actual = [file['path'].rpartition('/')[2] for file in client.list_files(path)]
        expected = [file['name'] for file in json.loads(RedisClient.get().get(f"results/{task.guid}")) if file['exists']]
        newline = '\n'
        logger.debug(f"Expected results for task {task.guid}: {newline.join(expected)}")
        logger.debug(f"Actual results for task {task.guid}: {newline.join(actual)}")

        if not set(expected).issubset(set(actual)):
            message = f"Transfer to CyVerse directory {path} incomplete: expected {len(expected)} files but found {len(actual)}"
            logger.warning(message)

            # mark the task failed
            now = timezone.now()
            task.updated = now
            task.completed = now
            task.status = TaskStatus.FAILURE
            task.transferred = True
            task.results_transferred = len(expected)
            task.save()
        else:
            message = f"Transfer to CyVerse directory {path} completed"
            logger.info(message)

            # mark the task succeeded
            now = timezone.now()
            task.updated = now
            task.completed = now
            task.status = TaskStatus.COMPLETED if task.status != TaskStatus.FAILURE else task.status
            task.transferred = True
            task.results_transferred = len(expected)
            task.save()

        # log status update and push it to clients
        # log_task_status(task, [message])
        # async_to_sync(push_task_channel_event)(task)

        return guid
    except Exception:
        self.request.callbacks = None
        message = f"Failed to test CyVerse transfer: {traceback.format_exc()}"

        # mark the task failed and persist it
        task.status = TaskStatus.FAILURE
        now = timezone.now()
        task.updated = now
        task.completed = now
        task.save()

        # log status update and push it to client
        log_task_status(task, [message])
        async_to_sync(push_task_channel_event)(task)

        # push AWS SNS notification
        if task.user.profile.push_notification_status == 'enabled':
            SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT task {task.guid}", message, {})

        # revoke access to the user's datasets then clean up the task
        unshare_data.s(task.guid).apply_async()
        tidy_up.s(task.guid).apply_async(countdown=int(environ.get('TASKS_CLEANUP_MINUTES')) * 60)


@app.task(track_started=True, bind=True)
def unshare_data(self, guid: str):
    if guid is None:
        logger.debug(f"Aborting")
        self.request.callbacks = None
        return

    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        self.request.callbacks = None
        return

    if task.status == TaskStatus.CANCELED:
        logger.warning(f"Task {guid} cancelled, aborting")
        self.request.callbacks = None
        return

    # TODO if any other running tasks share the same outbound transfer path, don't unshare
    # ... or use iRODS tickets (after unblocked here: https://github.com/Computational-Plant-Science/plantit/issues/225)
    # if Task.objects \
    #         .filter(user=task.user, status__in=[TaskStatus.CREATED, TaskStatus.RUNNING], transfer_path=task.transfer_path) \
    #         .exclude(guid=task.guid) \
    #         .count() != 0:
    #     logger.warning(f"Task {guid} outbound path {task.transfer_path} used by another task, not revoking temporary data access")
    #     self.request.callbacks = None
    #     return guid

    logger.warning(f"Not revoking temporary data access for task {guid} outbound path {task.transfer_path}")
    return guid

    # if the admin user owns this task, we don't need to share/unshare datasets
    if task.user.username == settings.CYVERSE_USERNAME:
        logger.info(f"Admin user {settings.CYVERSE_USERNAME} owns task {guid}, no need to revoke temporary data access")

        # mark the task completed
        now = timezone.now()
        if task.status != TaskStatus.COMPLETED and task.status != TaskStatus.FAILURE:
            task.status = TaskStatus.COMPLETED
        task.updated = now
        task.completed = now
        task.save()

        log_task_status(task, [f"Task {task.guid} completed"])
        async_to_sync(push_task_channel_event)(task)

        return guid

    try:
        options = task.workflow
        paths = [options['output']['to']]
        # if the input is a publicly shared directory, no need to revoke access (the request would fail anyway)
        if 'input' in options and '/iplant/home/shared' not in options['input']['path']:
            paths.append(options['input']['path'])

        # revoke the plantit CyVerse user's access to the source and target collections
        client = TerrainClient(access_token=task.user.profile.cyverse_access_token)
        client.unshare_many(username=task.user.username, paths=paths)

        # log_task_status(task, [f"Revoked temporary data access"])
        # async_to_sync(push_task_channel_event)(task)

        # mark the task completed
        now = timezone.now()
        if task.status != TaskStatus.COMPLETED and task.status != TaskStatus.FAILURE:
            task.status = TaskStatus.COMPLETED
        task.updated = now
        task.completed = now
        task.save()

        log_task_status(task, [f"Task {task.guid} completed"])
        async_to_sync(push_task_channel_event)(task)

        return guid
    except Exception:
        self.request.callbacks = None
        message = f"Failed to revoke temporary data access: {traceback.format_exc()}"
        logger.error(message)

        # mark the task failed and persist it
        task.status = TaskStatus.FAILURE
        now = timezone.now()
        task.updated = now
        task.completed = now
        task.save()

        # log status update and push it to client
        # log_task_status(task, [message])
        # async_to_sync(push_task_channel_event)(task)

        # push AWS SNS notification
        if task.user.profile.push_notification_status == 'enabled':
            SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT task {task.guid}", message, {})

        # clean up the task
        tidy_up.s(task.guid).apply_async(countdown=int(environ.get('TASKS_CLEANUP_MINUTES')) * 60)


@app.task()
def tidy_up(guid: str):
    if guid is None:
        logger.debug(f"Aborting")
        return

    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        return

    try:
        # logger.info(f"Cleaning up task with GUID {guid} local working directory {task.agent.workdir}")
        # remove_task_orchestration_logs(task)

        logger.info(f"Cleaning up task with GUID {guid} remote working directory {task.agent.workdir}")
        command = f"rm -rf {join(task.agent.workdir, task.workdir)}"
        ssh = get_task_ssh_client(task)
        with ssh:
            for line in execute_command(ssh=ssh, setup_command=task.agent.pre_commands, command=command, directory=task.agent.workdir,
                                        allow_stderr=True):
                logger.info(f"[{task.agent.name}] {line}")

        task.cleaned_up = True
        task.save()

        log_task_status(task, [f"Cleaned up"])
        async_to_sync(push_task_channel_event)(task)
    except Exception:
        logger.error(f"Failed to clean up: {traceback.format_exc()}")


# Miscellaneous Tasks
#
# These should only run one at a time (i.e., should not overlap).
# To prevent overlap we use the Django cache as a lock mechanism,
# as described here:
# https://docs.celeryproject.org/en/2.4/tutorials/task-cookbook.html#cookbook-task-serial

LOCK_EXPIRE = 60 * 5  # Lock expires in 5 minutes


def __acquire_lock(name):
    return cache.add(name, True, LOCK_EXPIRE)


def __release_lock(name):
    return cache.delete(name)


@app.task()
def find_stranded():
    task_name = find_stranded.name
    if not __acquire_lock(task_name):
        logger.warning(f"Task '{task_name}' is already running, aborting (maybe consider a longer scheduling interval?)")
        return

    try:
        # check if any running tasks haven't been updated in a while
        running = Task.objects.filter(status=TaskStatus.RUNNING)
        for task in running:
            now = timezone.now()
            period = int(environ.get('TASKS_REFRESH_SECONDS'))

            # if the task is still running and hasn't been updated in the last 2 refresh cycles, it might be stranded
            if (now - task.updated).total_seconds() > (2 * period):
                logger.warning(f"Found possibly stranded task: {task.guid}")
            if (now - task.updated).total_seconds() > (5 * period):
                logger.info(f"Trying to rescue stranded task: {task.guid}")
                if task.job_id is not None:
                    poll_jobs.s(task.guid).apply_async(soft_time_limit=int(settings.TASKS_STEP_TIME_LIMIT_SECONDS))
                else:
                    logger.error(f"Couldn't rescue stranded task '{task.guid}' (no job ID)")
    finally:
        __release_lock(task_name)


@app.task()
def refresh_all_users_stats():
    task_name = refresh_all_users_stats.name
    if not __acquire_lock(task_name):
        logger.warning(f"Task '{task_name}' is already running, aborting (maybe consider a longer scheduling interval?)")
        return

    try:
        # TODO: move caching to query layer
        redis = RedisClient.get()

        for user in User.objects.all():
            logger.info(f"Computing statistics for {user.username}")

            # overall statistics (no need to save result, just trigger reevaluation)
            async_to_sync(q.get_user_statistics)(user, True)

            # timeseries (no need to save result, just trigger reevaluation)
            q.get_user_timeseries(user, invalidate=True)

        logger.info(f"Computing aggregate statistics")
        redis.set("stats_counts", json.dumps(q.get_total_counts(True)))
        redis.set("total_timeseries", json.dumps(q.get_aggregate_timeseries(True)))
    finally:
        __release_lock(task_name)


@app.task()
def refresh_user_stats(username: str):
    task_name = refresh_user_stats.name
    if not __acquire_lock(task_name):
        logger.warning(f"Task '{task_name}' is already running, aborting (maybe consider a longer scheduling interval?)")
        return

    try:
        user = User.objects.get(username=username)
    except:
        logger.warning(f"User {username} not found: {traceback.format_exc()}")
        __release_lock(task_name)
        return

    try:
        logger.info(f"Aggregating statistics for {user.username}")

        # overall statistics (no need to save result, just trigger reevaluation)
        async_to_sync(q.get_user_statistics)(user, True)

        # timeseries (no need to save result, just trigger reevaluation)
        q.get_user_timeseries(user, invalidate=True)
    finally:
        __release_lock(task_name)


@app.task()
def refresh_user_workflows(owner: str):
    task_name = refresh_user_workflows.name
    if not __acquire_lock(task_name):
        logger.warning(f"Task '{task_name}' is already running, aborting (maybe consider a longer scheduling interval?)")
        return

    try:
        async_to_sync(refresh_user_workflow_cache)(owner)
    finally:
        __release_lock(task_name)


@app.task()
def refresh_all_workflows():
    task_name = refresh_all_workflows.name
    if not __acquire_lock(task_name):
        logger.warning(f"Task '{task_name}' is already running, aborting (maybe consider a longer scheduling interval?)")
        return

    try:
        async_to_sync(refresh_online_users_workflow_cache)()
        async_to_sync(refresh_online_user_orgs_workflow_cache)()
    finally:
        __release_lock(task_name)


@app.task()
def refresh_user_institutions():
    task_name = refresh_user_institutions.name
    if not __acquire_lock(task_name):
        logger.warning(f"Task '{task_name}' is already running, aborting (maybe consider a longer scheduling interval?)")
        return

    try:
        # TODO: move caching to query layer
        redis = RedisClient.get()
        institutions = q.get_institutions(True)
        for name, institution in institutions.items(): redis.set(f"institutions/{name}", json.dumps(institution))
    finally:
        __release_lock(task_name)


@app.task()
def refresh_cyverse_tokens(username: str):
    task_name = refresh_cyverse_tokens.name
    if not __acquire_lock(task_name):
        logger.warning(f"Task '{task_name}' is already running, aborting (maybe consider a longer scheduling interval?)")
        return

    try:
        user = User.objects.get(username=username)
    except:
        logger.warning(f"User {username} not found: {traceback.format_exc()}")
        __release_lock(task_name)
        return

    try:
        refresh_user_cyverse_tokens(user)
    finally:
        __release_lock(task_name)


@app.task()
def refresh_all_user_cyverse_tokens():
    task_name = refresh_all_user_cyverse_tokens.name
    if not __acquire_lock(task_name):
        logger.warning(f"Task '{task_name}' is already running, aborting (maybe consider a longer scheduling interval?)")
        return

    try:
        tasks = Task.objects.filter(status=TaskStatus.RUNNING)
        users = [task.user for task in list(tasks)]

        if len(users) == 0:
            logger.info(f"No users with running tasks, not refreshing CyVerse tokens")
            return

        group([refresh_cyverse_tokens.s(user.username) for user in users])()
        logger.info(f"Refreshed CyVerse tokens for {len(users)} user(s)")
    finally:
        __release_lock(task_name)


@app.task()
def agents_healthchecks():
    task_name = agents_healthchecks.name
    if not __acquire_lock(task_name):
        logger.warning(f"Task '{task_name}' is already running, aborting (maybe consider a longer scheduling interval?)")
        return

    try:
        for agent in Agent.objects.all():
            healthy, output = is_healthy(agent)
            plantit.healthchecks.is_healthy = healthy
            agent.save()

            redis = RedisClient.get()
            length = redis.llen(f"healthchecks/{agent.name}")
            checks_saved = int(settings.AGENTS_HEALTHCHECKS_SAVED)
            if length > checks_saved: redis.rpop(f"healthchecks/{agent.name}")
            check = {
                'timestamp': timezone.now().isoformat(),
                'healthy': healthy,
                'output': output
            }
            redis.lpush(f"healthchecks/{agent.name}", json.dumps(check))
    finally:
        __release_lock(task_name)


# DIRT migration


@app.task(bind=True)
def transfer_dirt_file(self, id):
    try:
        file = ManagedFile.objects.get(id=id)
        migration = file.migration
        profile = migration.profile
        user = profile.user
    except:
        logger.warning(f"Couldn't find DIRT managed file with id {id}, aborting")
        return

    logger.info(f"Downloading file from {file.nfs_path} to {file.staging_path}")

    try:
        ssh = SSH(
            host=settings.DIRT_MIGRATION_HOST,
            port=settings.DIRT_MIGRATION_PORT,
            username=settings.DIRT_MIGRATION_USERNAME,
            pkey=str(get_user_private_key_path(settings.DIRT_MIGRATION_USERNAME)))
        with ssh:
            with ssh.client.open_sftp() as sftp:
                sftp.get(file.nfs_path, file.staging_path)
    except FileNotFoundError:
        logger.warning(f"File {file.nfs_path} not found! Skipping")
        file.missing = True
        file.save()
        async_to_sync(mig.push_migration_event)(user, migration, file)

    logger.info(f"Uploading file from {file.staging_path} to collection {file.collection}")

    # create client for CyVerse APIs and create collection for migrated DIRT data
    client = TerrainClient(access_token=profile.cyverse_access_token, timeout_seconds=600)  # 10-min long timeout for large image files
    client.upload(from_path=file.staging_path, to_prefix=file.collection)  # upload the file to the corresponding collection

    # persist managed file record
    file.uploaded = timezone.now()
    file.save()

    # remove file from staging dir
    os.remove(file.staging_path)

    # get CyVerse data store ID of newly uploaded file, then get metadata and environmental data from DIRT and attach it as metadata
    stat = client.stat(join(file.collection, file.name))
    id = stat['id']
    metadata, resolution, age, dry_biomass, fresh_biomass, family, genus, spad, species = mig.get_root_image_info(file.entity_id)
    props = [f"migrated={timezone.now().isoformat()}"]
    if resolution is not None: props.append(f"resolution={resolution}")
    if age is not None: props.append(f"age={age}")
    if dry_biomass is not None: props.append(f"dry_biomass={dry_biomass}")
    if fresh_biomass is not None: props.append(f"fresh_biomass={fresh_biomass}")
    if family is not None: props.append(f"family={family}")
    if genus is not None: props.append(f"genus={genus}")
    if spad is not None: props.append(f"spad={spad}")
    if species is not None: props.append(f"species={species}")
    for k, v in metadata.items(): props.append(f"{k}={v}")
    client.set_metadata(id, props, [])

    # push an update to client
    async_to_sync(mig.push_migration_event)(user, migration, file)


@app.task(bind=True)
def start_dirt_migration(self, username: str):
    try:
        user = User.objects.get(username=username)
        profile = Profile.objects.get(user=user)
        migration = Migration.objects.get(profile=profile)
    except:
        logger.warning(f"Couldn't find DIRT migration info for user {username}, aborting")
        self.request.callbacks = None
        return

    # persist user's DIRT username
    dirt_username = user.username if profile.dirt_name is None else profile.dirt_name
    if dirt_username == 'wbonelli': dirt_username = 'abucksch'  # debugging
    migration.dirt_username = dirt_username
    migration.save()

    rootnfs_dir = join(settings.DIRT_MIGRATION_DATA_DIR, dirt_username)  # DIRT NFS path
    staging_dir = join(settings.DIRT_MIGRATION_STAGING_DIR, user.username)  # local staging folder for this user
    Path(staging_dir).mkdir(parents=True, exist_ok=True)

    # create client for CyVerse science API
    client = TerrainClient(access_token=profile.cyverse_access_token, timeout_seconds=600)  # 10-min long timeout for large image files
    migration_collection_path = f"/iplant/home/{user.username}/dirt_migration"
    if client.dir_exists(migration_collection_path):
        logger.warning(f"Collection {migration_collection_path} already exists, aborting DIRT migration for {user.username}")
        return

    # create top-level collection for transferred DIRT data
    client.mkdir(migration_collection_path)

    # get ID of newly created migration collection add collection timestamp as metadata
    root_collection_id = client.stat(migration_collection_path)['id']
    end = timezone.now()
    client.set_metadata(root_collection_id, [
        f"dirt_migration_started={end.isoformat()}",
        # TODO: anything else we need to add here?
    ], [])

    # create subcollections for root image sets, image metadata, computation outputs and logs
    client.mkdir(join(migration_collection_path, 'collections'))
    client.mkdir(join(migration_collection_path, 'metadata'))
    client.mkdir(join(migration_collection_path, 'outputs'))
    client.mkdir(join(migration_collection_path, 'logs'))

    # get all managed files from DIRT database and separate by type
    managed_files = mig.get_managed_files(dirt_username)
    image_files = [f for f in managed_files if f.type == 'image']
    metadata_files = [f for f in managed_files if f.type == 'metadata']
    output_files = [f for f in managed_files if f.type == 'output']
    log_files = [f for f in managed_files if f.type == 'logs']

    # create collections in CyVerse data store and attach metadata
    collections_created = set()
    for file in image_files:
        # get file entity ID given root image file ID
        file_entity_id = mig.get_file_entity_id(file.id)

        # if no corresponding file entity for this managed file, skip it
        if file_entity_id is None:
            logger.warning(f"DIRT root image with file ID {file.id} not found")
            continue

        # get collection entity ID for the collection this image is in
        collection_entity_id = mig.get_collection_entity_id(file_entity_id)

        # if no corresponding marked collection for this image, use an orphan folder named by date (as stored on the DIRT server NFS)
        if collection_entity_id is None:
            logger.warning(f"DIRT root image collection with entity ID {file_entity_id} not found")

            # create the collection if we need to
            collection_path = join(migration_collection_path, 'collections', file.folder)
            if file.folder not in collections_created:
                # mark this collection as seen
                collections_created.add(file.folder)

                # create the collection in the data store
                logger.info(f"Creating DIRT migration subcollection {collection_path}")
                client.mkdir(collection_path)

        # otherwise we have a corresponding marked collection, get its title
        collection_name, collection_created, collection_changed = mig.get_marked_collection(collection_entity_id)
        collection_path = join(migration_collection_path, 'collections', collection_name)

        if collection_name not in collections_created:
            collections_created.add(collection_name)

            # create the collection in the data store
            logger.info(f"Creating DIRT migration subcollection {collection_path}")
            client.mkdir(collection_path)

            # get CyVerse ID of newly created collection
            stat = client.stat(collection_path)
            id = stat['id']
            file.collection_datastore_id = id

            # get metadata and environmental data and attach to file
            metadata, lat, lon, planting, harvest, soil_group, soil_moist, soil_n, soil_p, soil_k, pesticides = mig.get_marked_collection_info(
                collection_entity_id)
            props = [
                f"migrated={timezone.now().isoformat()}",
                f"created={collection_created.isoformat()}",
                f"changed={collection_changed.isoformat()}",
            ]
            if lat is not None: props.append(f"latitude={lat}")
            if lon is not None: props.append(f"longitude={lon}")
            if planting is not None: props.append(f"planting={planting}")
            if harvest is not None: props.append(f"harvest={harvest}")
            if soil_group is not None: props.append(f"soil_group={soil_group}")
            if soil_moist is not None: props.append(f"soil_moisture={soil_moist}")
            if soil_n is not None: props.append(f"soil_nitrogen={soil_n}")
            if soil_p is not None: props.append(f"soil_phosphorus={soil_p}")
            if soil_k is not None: props.append(f"soil_potassium={soil_k}")
            if pesticides is not None: props.append(f"pesticides={pesticides}")
            for k, v in metadata.items(): props.append(f"{k}={v}")
            client.set_metadata(id, props, [])

        # persist collection information on managed file record
        file.collection = collection_name
        file.collection_entity_id = collection_entity_id

        # create managed file record
        file_rec = ManagedFile.objects.create(migration=migration,
                                              name=file.name,
                                              folder=file.folder,
                                              path=file.path,
                                              type=file.type,
                                              orphan=file.orphan,
                                              missing=file.missing,
                                              uploaded=file.uploaded,
                                              nfs_path=join(rootnfs_dir, 'root-images', file.folder, file.name),
                                              staging_path=join(staging_dir, file.name))
    for file in metadata_files:
        # create the subcollection if we need to
        collection_path = join(migration_collection_path, 'metadata', file.folder)
        if file.folder not in collections_created:
            collections_created.add(file.folder)
            logger.info(f"Creating DIRT migration metadata subcollection {collection_path}")
            client.mkdir(collection_path)

        # create managed file record
        file_rec = ManagedFile.objects.create(migration=migration,
                                              name=file.name,
                                              folder=file.folder,
                                              path=file.path,
                                              type=file.type,
                                              orphan=file.orphan,
                                              missing=file.missing,
                                              uploaded=file.uploaded,
                                              nfs_path=join(rootnfs_dir, 'metadata-files', file.folder, file.name),
                                              staging_path=join(staging_dir, file.name))
    for file in output_files:
        # create the folder if we need to
        collection_path = join(migration_collection_path, 'outputs', file.folder)
        if file.folder not in collections_created:
            collections_created.add(file.folder)
            logger.info(f"Creating DIRT migration outputs subcollection {collection_path}")
            client.mkdir(collection_path)

        # create managed file record
        file_rec = ManagedFile.objects.create(migration=migration,
                                              name=file.name,
                                              folder=file.folder,
                                              path=file.path,
                                              type=file.type,
                                              orphan=file.orphan,
                                              missing=file.missing,
                                              uploaded=file.uploaded,
                                              nfs_path=join(rootnfs_dir, 'output-files', file.folder, file.name),
                                              staging_path=join(staging_dir, file.name))
    for file in log_files:
        # create the folder if we need to
        collection_path = join(migration_collection_path, 'logs', file.folder)
        if file.folder not in collections_created:
            collections_created.add(file.folder)
            logger.info(f"Creating DIRT migration logs subcollection {collection_path}")
            client.mkdir(collection_path)

        # create managed file record
        file_rec = ManagedFile.objects.create(migration=migration,
                                              name=file.name,
                                              folder=file.folder,
                                              path=file.path,
                                              type=file.type,
                                              orphan=file.orphan,
                                              missing=file.missing,
                                              uploaded=file.uploaded,
                                              nfs_path=join(rootnfs_dir, 'output-logs', file.folder, file.name),
                                              staging_path=join(staging_dir, file.name))

    # submit file transfers
    transfers = group(transfer_dirt_file(file) for file in managed_files)()
    transfers.apply_async()

    # persist number of each kind of managed file
    migration.num_files = len(image_files)
    migration.num_metadata = len(metadata_files)
    migration.num_outputs = len(output_files)
    migration.num_logs = len(log_files)
    migration.save()


# @app.task(bind=True)
# def complete_dirt_migration(self, username: str):
#     try:
#         user = User.objects.get(username=username)
#         profile = Profile.objects.get(user=user)
#         migration = Migration.objects.get(profile=profile)
#     except:
#         logger.warning(f"Couldn't find DIRT migration info for user {username}, aborting")
#         self.request.callbacks = None
#         return
#
#     # create client for CyVerse APIs and create collection for migrated DIRT data
#     client = TerrainClient(access_token=profile.cyverse_access_token, timeout_seconds=600)  # 10-min long timeout for large image files
#     root_collection_path = f"/iplant/home/{user.username}/dirt_migration"
#
#     # get ID of newly created migration collection add collection timestamp as metadata
#     root_collection_id = client.stat(root_collection_path)['id']
#     end = timezone.now()
#     client.set_metadata(root_collection_id, [
#         f"dirt_migration_started={end.isoformat()}",
#         # TODO: anything else we need to add here?
#     ], [])
#
#     # persist completion
#     completed = timezone.now()
#     migration.completed = completed
#     migration.save()
#
#     # push completion update to the UI
#     async_to_sync(mig.push_migration_event)(user, migration)
#
#     # send notification to user via email
#     SnsClient.get().publish_message(
#         profile.push_notification_topic_arn,
#         f"DIRT => PlantIT migration completed",
#         f"Duration: {str(end - migration.started)}",
#         {})


# see https://stackoverflow.com/a/41119054/6514033
# `@app.on_after_finalize.connect` is necessary for some reason instead of `@app.on_after_configure.connect`
@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    logger.info("Scheduling periodic tasks")
    sender.add_periodic_task(int(settings.CYVERSE_TOKEN_REFRESH_MINUTES) * 60, refresh_all_user_cyverse_tokens.s(), name='refresh CyVerse tokens')
    sender.add_periodic_task(int(settings.MAPBOX_FEATURE_REFRESH_MINUTES) * 60, refresh_user_institutions.s(), name='refresh user institutions')
    sender.add_periodic_task(int(settings.USERS_STATS_REFRESH_MINUTES) * 60, refresh_all_users_stats.s(), name='refresh user statistics')
    sender.add_periodic_task(int(settings.AGENTS_HEALTHCHECKS_MINUTES) * 60, agents_healthchecks.s(), name='check agent connections')
    sender.add_periodic_task(int(settings.WORKFLOWS_REFRESH_MINUTES) * 60, refresh_all_workflows.s(), name='refresh workflows cache')
    sender.add_periodic_task(int(settings.TASKS_REFRESH_SECONDS), find_stranded, name='check for stranded tasks')
