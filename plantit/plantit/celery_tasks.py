import json
import traceback
from datetime import timedelta, datetime
from os import environ
from os.path import join

import requests
from asgiref.sync import async_to_sync
from celery import group
from celery.utils.log import get_task_logger
from django.contrib.auth.models import User
from django.utils import timezone

import plantit.healthchecks
import plantit.mapbox
import plantit.queries as q
import plantit.terrain as terrain
import plantit.utils.agents
from plantit import settings
from plantit.agents.models import Agent
from plantit.celery import app
from plantit.healthchecks import is_healthy
from plantit.queries import refresh_user_workflow_cache, refresh_online_users_workflow_cache, refresh_online_user_orgs_workflow_cache, \
    refresh_user_cyverse_tokens
from plantit.redis import RedisClient
from plantit.sns import SnsClient
from plantit.ssh import execute_command
from plantit.task_lifecycle import create_immediate_task, configure_task_environment, submit_task_to_scheduler, check_job_logs_for_progress, \
    get_job_status_and_walltime, list_result_files, cancel_task
from plantit.task_resources import get_task_ssh_client, push_task_channel_event, log_task_orchestrator_status, get_task_remote_logs
from plantit.tasks.models import Task, TaskStatus

logger = get_task_logger(__name__)


def report_failed_and_schedule_cleanup(task: Task, step: str):
    # mark the task failed
    task.status = TaskStatus.FAILURE
    now = timezone.now()
    task.updated = now
    task.completed = now
    task.save()

    # there was an unexpected exception somewhere, catch and log it
    message = f"Task '{task.guid}' step '{step}' job '{task.job_id}' failed: {traceback.format_exc()}"
    log_task_orchestrator_status(task, [message])
    async_to_sync(push_task_channel_event)(task)

    # schedule cleanup
    cleanup_delay = int(environ.get('TASKS_CLEANUP_MINUTES')) * 60
    tidy_up.s(task.guid).apply_async(countdown=cleanup_delay, priority=2)
    task.cleanup_time = timezone.now() + timedelta(seconds=cleanup_delay)
    task.save()

    # push AWS SNS notification
    if task.user.profile.push_notification_status == 'enabled':
        SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn,
                                        f"PlantIT task {task.guid}",
                                        message, {})


# Task lifecycle:
#   prep environment
#   submit executable/run script
#   poll status until complete
#   check results
#   check CyVerse transfer
#   clean up


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

    # submit head of Celery (chain ;)
    prep_environment.s(task.guid).apply_async(soft_time_limit=int(settings.TASKS_STEP_TIME_LIMIT_SECONDS))


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

    # submit head of Celery (chain ;)
    prep_environment.s(task.guid).apply_async(soft_time_limit=int(settings.TASKS_STEP_TIME_LIMIT_SECONDS))


@app.task(track_started=True)
def prep_environment(guid: str):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        return

    try:
        log_task_orchestrator_status(task, [f"Preparing environment for {task.user.username}'s task {task.guid} on {task.agent.name}"])
        async_to_sync(push_task_channel_event)(task)
        configure_task_environment(task)

        # submit next Celery task in the chain
        send_pull.s(guid).apply_async(soft_time_limit=int(settings.TASKS_STEP_TIME_LIMIT_SECONDS))
    except Exception:
        report_failed_and_schedule_cleanup(task, 'prep environment')


@app.task(track_started=True)
def send_pull(guid: str):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        return

    try:
        # submit next Celery task in the chain
        poll_pull.s(guid).apply_async(soft_time_limit=int(settings.TASKS_STEP_TIME_LIMIT_SECONDS))
    except:
        report_failed_and_schedule_cleanup(task, 'send pull')


@app.task(track_started=True)
def poll_pull(guid: str):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        return

    refresh_delay = int(environ.get('TASKS_REFRESH_SECONDS'))
    logger.info(f"Checking {task.agent.name} scheduler status for task {guid} (job {task.job_id})")

    # otherwise poll the scheduler for job status and walltime and update the task
    try:
        # get the job status from the scheduler
        check_job_logs_for_progress(task)
        job_status, job_walltime = get_job_status_and_walltime(task)

        # get_job_status() returns None if the job isn't found in the agent's scheduler.
        # there are 2 reasons this might happen:
        #   - the job was just submitted and hasn't been picked up for reporting by the scheduler yet
        #   - the job already completed and we waited too long between polls to check its status
        #
        # in both cases we return early
        if job_status is None:
            # we might have just submitted the job; scheduler may take a moment to reflect new submissions
            if not (task.job_status == 'COMPLETED' or task.job_status == 'COMPLETING'):
                # update the task and persist it
                now = timezone.now()
                task.updated = now
                task.job_status = job_status
                task.job_consumed_walltime = job_walltime
                task.save()
                retry_seconds = 10

                # log the status update and push it to clients
                message = f"Job {task.job_id} not found, retrying in {retry_seconds} seconds"
                log_task_orchestrator_status(task, [message])
                async_to_sync(push_task_channel_event)(task)

                # wait a few seconds and poll again
                poll_containers.s(guid).apply_async(countdown=retry_seconds)
                return
            # otherwise the job completed and the scheduler's forgotten about it in the interval between polls
            else:
                # update the task and persist it
                now = timezone.now()
                task.updated = now
                task.job_status = 'COMPLETED'
                task.job_consumed_walltime = job_walltime
                task.save()

                # check that we have the results we expect
                test_results.s(guid).apply_async()

                # log the status update and push it to clients
                message = f"Job {task.job_id} completed with unknown status" + (f" after {job_walltime}" if job_walltime is not None else '')
                log_task_orchestrator_status(task, [message])
                async_to_sync(push_task_channel_event)(task)

                # push AWS SNS notification
                if task.user.profile.push_notification_status == 'enabled':
                    SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT task {task.guid}", message, {})

            return

        # update the task and persist it
        task.job_status = job_status
        task.job_consumed_walltime = job_walltime
        now = timezone.now()
        task.updated = now
        task.save()

        # get remote log files
        ssh = get_task_ssh_client(task)
        get_task_remote_logs(task, ssh)

        # if completed unsuccessfully, mark the task according to its failure mode
        job_complete = False
        if job_status == 'FAILED':
            task.status = TaskStatus.FAILURE
            job_complete = True
        elif job_status == 'CANCELLED':
            task.status = TaskStatus.CANCELED
            job_complete = True
        elif job_status == 'TIMEOUT':
            task.status = TaskStatus.TIMEOUT
            job_complete = True
        # but if it succeeded, we still need to check results before determining success/failure
        elif job_status == 'COMPLETED':
            job_complete = True

        # update the task and persist it
        now = timezone.now()
        task.updated = now
        task.save()

        if job_complete:
            send_containers.s(guid).apply_async()

            # log the status update and push it to clients
            message = f"Task {task.guid} pull job {task.job_id} completed with status {job_status}" + (f" after {job_walltime}" if job_walltime is not None else '')
            log_task_orchestrator_status(task, [message])
            async_to_sync(push_task_channel_event)(task)

            # push AWS SNS notification
            if task.user.profile.push_notification_status == 'enabled':
                SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT task {task.guid}", message, {})

            return
        else:
            # if past due time...
            if now > task.due_time:
                # log the status update and push it to clients
                message = f"Task {task.guid} pull job {task.job_id} {job_status} (walltime {job_walltime}) is past its due time {str(task.due_time)}"
                log_task_orchestrator_status(task, [message])
                async_to_sync(push_task_channel_event)(task)

                # cancel the task
                cancel_task(task)
            else:
                # log the status update and push it to clients
                message = f"Task {task.guid} pull job {task.job_id} {job_status} (walltime {job_walltime})"
                log_task_orchestrator_status(task, [message])
                async_to_sync(push_task_channel_event)(task)

                # otherwise schedule another round of polling
                poll_containers.s(guid).apply_async(countdown=refresh_delay)
    except:
        report_failed_and_schedule_cleanup(task, 'poll pull')


@app.task(track_started=True, bind=True)
def send_containers(self, guid: str):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        self.request.callbacks = None  # stop the task chain
        return

    # if the task already failed or the current scheduler job failed, skip to end of pipeline
    if task.status == TaskStatus.FAILURE or task.job_status == 'FAILURE':
        return skip_failed(task, 'send containers')

    # mark the task running
    task.status = TaskStatus.RUNNING
    task.celery_task_id = self.request.id  # set the Celery task's ID so user can cancel
    task.save()

    try:
        ssh = get_task_ssh_client(task)
        with ssh:
            # schedule the job
            job_id = submit_task_to_scheduler(task, ssh)
            log_task_orchestrator_status(task, [f"Scheduled task as job {job_id}"])
            async_to_sync(push_task_channel_event)(task)
            return guid
    except Exception:
        # mark task failed
        task.status = TaskStatus.FAILURE
        now = timezone.now()
        task.updated = now
        task.completed = now
        task.save()

        # log status and update the client
        error = traceback.format_exc()
        log_task_orchestrator_status(task, [f"Failed with error: {error}"])
        logger.error(f"Failed to submit task {task.guid}  on {task.agent.name}: {error}")
        async_to_sync(push_task_channel_event)(task)

        # stop the task chain
        self.request.callbacks = None


@app.task(bind=True)
def poll_containers(self, guid: str):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        self.request.callbacks = None  # stop the task chain
        return

    # if the task already failed or the current scheduler job failed, skip to end of pipeline
    if task.status == TaskStatus.FAILURE or task.job_status == 'FAILURE':
        return skip_failed(task, 'poll containers')

    refresh_delay = int(environ.get('TASKS_REFRESH_SECONDS'))
    logger.info(f"Checking {task.agent.name} scheduler status for task {guid} (job {task.job_id})")

    # poll the scheduler for job status and walltime and update the task
    try:
        # get the job status from the scheduler
        check_job_logs_for_progress(task)
        job_status, job_walltime = get_job_status_and_walltime(task)

        # get_job_status() returns None if the job isn't found in the agent's scheduler.
        # there are 2 reasons this might happen:
        #   - the job was just submitted and hasn't been picked up for reporting by the scheduler yet
        #   - the job already completed and we waited too long between polls to check its status
        #
        # in both cases we return early
        if job_status is None:
            # we might have just submitted the job; scheduler may take a moment to reflect new submissions
            if not (task.job_status == 'COMPLETED' or task.job_status == 'COMPLETING'):
                # update the task and persist it
                now = timezone.now()
                task.updated = now
                task.job_status = job_status
                task.job_consumed_walltime = job_walltime
                task.save()
                retry_seconds = 10

                # log the status update and push it to clients
                message = f"Job {task.job_id} not found, retrying in {retry_seconds} seconds"
                log_task_orchestrator_status(task, [message])
                async_to_sync(push_task_channel_event)(task)

                # wait a few seconds and poll again
                poll_containers.s(guid).apply_async(countdown=retry_seconds)
                return
            # otherwise the job completed and the scheduler's forgotten about it in the interval between polls
            else:
                # update the task and persist it
                now = timezone.now()
                task.updated = now
                task.job_status = 'COMPLETED'
                task.job_consumed_walltime = job_walltime
                task.save()

                # check that we have the results we expect
                test_results.s(guid).apply_async()

                # log the status update and push it to clients
                message = f"Job {task.job_id} completed with unknown status" + (f" after {job_walltime}" if job_walltime is not None else '')
                log_task_orchestrator_status(task, [message])
                async_to_sync(push_task_channel_event)(task)

                # push AWS SNS notification
                if task.user.profile.push_notification_status == 'enabled':
                    SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT task {task.guid}", message, {})

            return guid

        # update the task and persist it
        task.job_status = job_status
        task.job_consumed_walltime = job_walltime
        now = timezone.now()
        task.updated = now
        task.save()

        # get remote log files
        ssh = get_task_ssh_client(task)
        get_task_remote_logs(task, ssh)

        # if job did not complete, go ahead and mark the task failed/cancelled/timed out/etc
        job_complete = False
        if job_status == 'FAILED':
            task.status = TaskStatus.FAILURE
            job_complete = True
        elif job_status == 'CANCELLED':
            task.status = TaskStatus.CANCELED
            job_complete = True
        elif job_status == 'TIMEOUT':
            task.status = TaskStatus.TIMEOUT
            job_complete = True
        # but if it succeeded, we still need to check results before determining success/failure
        elif job_status == 'COMPLETED':
            job_complete = True

        # update the task and persist it
        now = timezone.now()
        task.updated = now
        task.save()

        if job_complete:
            # check that we have the results we expect
            test_results.s(guid).apply_async()

            # log the status update and push it to clients
            message = f"Job {task.job_id} completed with status {job_status}" + (f" after {job_walltime}" if job_walltime is not None else '')
            log_task_orchestrator_status(task, [message])
            async_to_sync(push_task_channel_event)(task)

            # push AWS SNS notification
            if task.user.profile.push_notification_status == 'enabled':
                SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT task {task.guid}", message, {})

            return guid
        else:
            # if past due time...
            if now > task.due_time:
                # log the status update and push it to clients
                message = f"Job {task.job_id} {job_status} (walltime {job_walltime}) is past its due time {str(task.due_time)}"
                log_task_orchestrator_status(task, [message])
                async_to_sync(push_task_channel_event)(task)

                # cancel the task
                cancel_task(task)
            else:
                # log the status update and push it to clients
                message = f"Job {task.job_id} {job_status} (walltime {job_walltime})"
                log_task_orchestrator_status(task, [message])
                async_to_sync(push_task_channel_event)(task)

                # otherwise schedule another round of polling
                poll_containers.s(guid).apply_async(countdown=refresh_delay)
    except:
        report_failed(task, 'poll containers')


def test_results(guid: str):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        return

    try:
        redis = RedisClient.get()
        ssh = get_task_ssh_client(task)

        # log status update and push it to clients
        message = f"Retrieving logs"
        log_task_orchestrator_status(task, [message])
        async_to_sync(push_task_channel_event)(task)

        # get logs from agent filesystem
        get_task_remote_logs(task, ssh)

        # log status update and push it to clients
        message = f"Retrieving results"
        log_task_orchestrator_status(task, [message])
        async_to_sync(push_task_channel_event)(task)

        # get results from agent filesystem, then save them to cache and update the task
        results = list_result_files(task)
        found = [r for r in results if r['exists']]
        missing = [r for r in results if not r['exists']]
        redis.set(f"results/{task.guid}", json.dumps(found))
        task.results_retrieved = True
        task.save()

        # make sure we got the results we expected
        if len(missing) > 0:
            # log status update and push it to clients
            message = f"Found {len(found)} results, missing {len(missing)}: {', '.join([m['name'] for m in missing])}"
            log_task_orchestrator_status(task, [message])
            async_to_sync(push_task_channel_event)(task)
        else:
            # log status update and push it to clients
            message = f"Found {len(found)} results"
            log_task_orchestrator_status(task, [message])
            async_to_sync(push_task_channel_event)(task)

        # log status update and push it to clients
        message = f"Verifying data was transferred to CyVerse"
        log_task_orchestrator_status(task, [message])
        async_to_sync(push_task_channel_event)(task)
    except Exception:
        pass


@app.task(track_started=True)
def send_push(guid: str):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        return

    # if the task already failed or the current scheduler job failed, skip to end of pipeline
    if task.status == TaskStatus.FAILURE or task.job_status == 'FAILURE':
        skip_failed(task, 'send push')

    try:
        # submit next Celery task in the chain
        poll_push.s(guid).apply_async(soft_time_limit=int(settings.TASKS_STEP_TIME_LIMIT_SECONDS))
    except Exception:
        pass


@app.task(track_started=True)
def poll_push(guid: str):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        return

    # if the task already failed or the current scheduler job failed, skip to end of pipeline
    if task.status == TaskStatus.FAILURE or task.job_status == 'FAILURE':
        skip_failed(task, 'poll push')

    try:
        # submit next Celery task in the chain
        test_push.s(guid).apply_async(soft_time_limit=int(settings.TASKS_STEP_TIME_LIMIT_SECONDS))
    except Exception:
        pass


@app.task()
def test_push(guid: str, attempts: int = 0):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        return

    # if the task already failed or the current scheduler job failed, skip to end of pipeline
    if task.status == TaskStatus.FAILURE or task.job_status == 'FAILURE':
        skip_failed(task, 'test push')

    try:
        # check the expected filenames against the contents of the CyVerse collection
        path = task.workflow['output']['to']
        actual = [file.rpartition('/')[2] for file in terrain.list_dir(path, task.user.profile.cyverse_access_token)]
        expected = [file['name'] for file in json.loads(RedisClient.get().get(f"results/{task.guid}"))]

        if not set(expected).issubset(set(actual)):
            logger.warning(f"Expected {len(expected)} uploads to CyVerse but found {len(actual)}")

            # TODO make this configurable
            max_attempts = 10
            countdown = 30

            if attempts < max_attempts:
                message = f"Transfer to CyVerse directory {path} incomplete, checking again in {countdown} seconds (attempt {attempts})"
                logger.warning(message)
                test_push.s(guid, attempts + 1).apply_async(countdown=countdown)
            else:
                message = f"Transfer to CyVerse directory {path} failed to complete after {attempts * countdown} seconds"
                logger.info(message)

                # mark the task failed
                now = timezone.now()
                task.updated = now
                task.completed = now
                task.status = TaskStatus.FAILURE
                task.transferred = True
                task.results_transferred = len(expected)
                task.transfer_path = path
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
            task.transfer_path = path
            task.save()

        # log status update and push it to clients
        log_task_orchestrator_status(task, [message])
        async_to_sync(push_task_channel_event)(task)

        # submit next Celery task in the chain
        tidy_up.s(guid).apply_async(soft_time_limit=int(settings.TASKS_STEP_TIME_LIMIT_SECONDS))
    except Exception:
        pass


@app.task()
def tidy_up(guid: str):
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
            for line in execute_command(ssh=ssh, precommand=task.agent.pre_commands, command=command, directory=task.agent.workdir, allow_stderr=True):
                logger.info(f"[{task.agent.name}] {line}")

        task.cleaned_up = True
        task.save()

        log_task_orchestrator_status(task, [f"Cleaned up task {task.guid}"])
        async_to_sync(push_task_channel_event)(task)
    except Exception:
        logger.error(f"Failed to clean up task {task.guid}: {traceback.format_exc()}")


@app.task()
def find_stranded():
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
            if task.pushed is not None:
                poll_push.s(task.guid).apply_async(soft_time_limit=int(settings.TASKS_STEP_TIME_LIMIT_SECONDS))
            elif task.worked is not None:
                poll_containers.s(task.guid).apply_async(soft_time_limit=int(settings.TASKS_STEP_TIME_LIMIT_SECONDS))
            elif task.pulled is not None:
                poll_pull.s(task.guid).apply_async(soft_time_limit=int(settings.TASKS_STEP_TIME_LIMIT_SECONDS))
            else:
                logger.error(f"Couldn't rescue stranded task '{task.guid}'")


@app.task()
def refresh_all_users_stats():
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


@app.task()
def refresh_user_stats(username: str):
    try:
        user = User.objects.get(username=username)
    except:
        logger.warning(f"User {username} not found: {traceback.format_exc()}")
        return

    logger.info(f"Aggregating statistics for {user.username}")

    # overall statistics (no need to save result, just trigger reevaluation)
    async_to_sync(q.get_user_statistics)(user, True)

    # timeseries (no need to save result, just trigger reevaluation)
    q.get_user_timeseries(user, invalidate=True)


@app.task()
def refresh_user_workflows(owner: str):
    async_to_sync(refresh_user_workflow_cache)(owner)


@app.task()
def refresh_all_workflows():
    async_to_sync(refresh_online_users_workflow_cache)()
    async_to_sync(refresh_online_user_orgs_workflow_cache)()


@app.task()
def refresh_user_institutions():
    # TODO: move caching to query layer

    redis = RedisClient.get()
    institutions = q.get_institutions(True)
    for name, institution in institutions.items(): redis.set(f"institutions/{name}", json.dumps(institution))


@app.task()
def refresh_cyverse_tokens(username: str):
    try:
        user = User.objects.get(username=username)
    except:
        logger.warning(f"User {username} not found: {traceback.format_exc()}")
        return

    refresh_user_cyverse_tokens(user)


@app.task()
def refresh_all_user_cyverse_tokens():
    tasks = Task.objects.filter(status=TaskStatus.RUNNING)
    users = [task.user for task in list(tasks)]

    if len(users) == 0:
        logger.info(f"No users with running tasks, not refreshing CyVerse tokens")
        return

    group([refresh_cyverse_tokens.s(user.username) for user in users])()
    logger.info(f"Refreshed CyVerse tokens for {len(users)} user(s)")


@app.task()
def agents_healthchecks():
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


class TerrainToken:
    __token = None

    @staticmethod
    def get():
        if TerrainToken.__token is not None:
            return TerrainToken.__token

        cyverse_username = environ.get('CYVERSE_USERNAME', None)
        cyverse_password = environ.get('CYVERSE_PASSWORD', None)

        if cyverse_username is None: raise ValueError("Missing environment variable 'CYVERSE_USERNAME'")
        if cyverse_password is None: raise ValueError("Missing environment variable 'CYVERSE_PASSWORD'")

        response = requests \
            .get('https://de.cyverse.org/terrain/token/cas', auth=(cyverse_username, cyverse_password)) \
            .json()

        TerrainToken.__token = response['access_token']
        return TerrainToken.__token


# see https://stackoverflow.com/a/41119054/6514033
# `@app.on_after_finalize.connect` is necessary for some reason instead of `@app.on_after_configure.connect`
@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    logger.info("Scheduling periodic tasks")

    # refresh CyVerse auth tokens for all users with running tasks (in case outputs need to get pushed on completion)
    sender.add_periodic_task(int(settings.CYVERSE_TOKEN_REFRESH_MINUTES) * 60, refresh_all_user_cyverse_tokens.s(),
                             name='refresh CyVerse tokens for users with running tasks')

    # refresh user institution geocoding info
    sender.add_periodic_task(int(settings.MAPBOX_FEATURE_REFRESH_MINUTES) * 60, refresh_user_institutions.s(), name='refresh user institutions')

    # aggregate usage stats for each user
    sender.add_periodic_task(int(settings.USERS_STATS_REFRESH_MINUTES) * 60, refresh_all_users_stats.s(), name='refresh user statistics')

    # agent healthchecks
    # TODO reenable with better scheduling strategy
    # sender.add_periodic_task(int(settings.AGENTS_HEALTHCHECKS_MINUTES) * 60, agents_healthchecks.s(), name='check agent connections', priority=1)

    # refresh workflow cache
    sender.add_periodic_task(int(settings.WORKFLOWS_REFRESH_MINUTES) * 60, refresh_all_workflows.s(), name='refresh workflows cache')

    # stranded task sweeps
    sender.add_periodic_task(int(settings.TASKS_REFRESH_SECONDS), find_stranded, name='check for stranded tasks')
