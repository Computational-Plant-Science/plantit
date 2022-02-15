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

    # submit to Celery
    (prep_environment.s(task.guid) | submit_job.s() | poll_job.s()).apply_async(countdown=5,  # TODO: make initial delay configurable
                                                                                soft_time_limit=int(settings.TASKS_STEP_TIME_LIMIT_SECONDS))


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

    # submit to Celery
    (prep_environment.s(task.guid) | submit_job.s() | poll_job.s()).apply_async(countdown=5,  # TODO: make initial delay configurable
                                                                                soft_time_limit=int(settings.TASKS_STEP_TIME_LIMIT_SECONDS))


##################
# task lifecycle #
##################
# prep environment
# submit script
# poll status
# check results
# check transfer
# clean up


def __handle_job_success(task: Task, message: str):
    # update the task and persist it
    now = timezone.now()
    task.updated = now
    task.job_status = 'COMPLETED'
    task.save()

    # log status to file
    log_task_orchestrator_status(task, [message])

    # push status to client(s)
    async_to_sync(push_task_channel_event)(task)

    # push AWS SNS notification
    if task.user.profile.push_notification_status == 'enabled':
        SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT task {task.guid}", message, {})

    # check that we have the results we expect and then clean up the task
    (test_results.s(task.guid) | tidy_up.s()).apply_async()


def __handle_failure(task: Task, message: str):
    # mark the task failed and persist it
    task.status = TaskStatus.FAILURE
    now = timezone.now()
    task.updated = now
    task.completed = now
    task.save()

    # log status to file
    log_task_orchestrator_status(task, [message])

    # push status to client(s)
    async_to_sync(push_task_channel_event)(task)

    # push AWS SNS notification
    if task.user.profile.push_notification_status == 'enabled':
        SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT task {task.guid}", message, {})

    # schedule cleanup
    tidy_up.s(task.guid).apply_async()

    # cleanup_delay = int(environ.get('TASKS_CLEANUP_MINUTES')) * 60
    # tidy_up.s(task.guid).apply_async(countdown=cleanup_delay, priority=2)
    # task.cleanup_time = timezone.now() + timedelta(seconds=cleanup_delay)
    # task.save()


@app.task(track_started=True, bind=True)
def prep_environment(self, guid: str):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        self.request.callbacks = None
        return

    try:
        # upload workflow and job script to deployment target
        configure_task_environment(task)
        log_task_orchestrator_status(task, [f"Prepared environment for {task.user.username}'s task {task.guid} on {task.agent.name}"])
        async_to_sync(push_task_channel_event)(task)

        return guid
    except Exception:
        self.request.callbacks = None
        __handle_failure(task, f"Failed to prep environment for task {task.guid}: {traceback.format_exc()}")


@app.task(track_started=True, bind=True)
def submit_job(self, guid: str):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        self.request.callbacks = None
        return

    try:
        # mark the task running
        task.status = TaskStatus.RUNNING
        task.celery_task_id = self.request.id  # set the Celery task's ID so user can cancel
        task.save()

        # submit the job to the cluster scheduler
        ssh = get_task_ssh_client(task)
        with ssh:
            job_id = submit_task_to_scheduler(task, ssh)
            log_task_orchestrator_status(task, [f"Scheduled task {guid} as job {job_id}"])
            async_to_sync(push_task_channel_event)(task)

        return guid
    except Exception:
        self.request.callbacks = None
        __handle_failure(task, f"Failed to submit job for task {task.guid}: {traceback.format_exc()}")


@app.task(track_started=True, bind=True)
def poll_job(self, guid: str):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        self.request.callbacks = None  # stop the task chain
        return

    # poll the scheduler for job status and walltime and update the task
    try:
        refresh_delay = int(environ.get('TASKS_REFRESH_SECONDS'))
        logger.info(f"Checking {task.agent.name} scheduler status for task {guid} (job {task.job_id})")

        # get the job status from the scheduler
        check_job_logs_for_progress(task)
        job_status, job_walltime = get_job_status_and_walltime(task)

        # get_job_status() returns None if the job isn't found in the agent's scheduler.
        # there are 2 reasons this might happen:
        #   - the job was just submitted and hasn't been picked up for reporting by the scheduler yet
        #   - the job already completed and we waited too long between polls to check its status
        if job_status is None:
            # update the task and persist it
            now = timezone.now()
            task.updated = now
            task.job_status = job_status
            task.job_consumed_walltime = job_walltime
            task.save()

            # we might have just submitted the job; scheduler may take a moment to reflect new submissions
            if not (task.job_status == 'COMPLETED' or task.job_status == 'COMPLETING'):
                # log the status update
                log_task_orchestrator_status(task, [f"Job {task.job_id} not found yet, retrying in {refresh_delay}s"])

                # push status to client(s)
                async_to_sync(push_task_channel_event)(task)

                # wait and poll again
                poll_job.s(guid).apply_async(countdown=refresh_delay)
            else:
                # otherwise the job completed and the scheduler's forgotten about it in the interval between polls
                __handle_job_success(task, f"Job {task.job_id} completed with unknown status" + (f" after {job_walltime}" if job_walltime is not None else ''))

            # in either case, return early
            return guid

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
        task.job_status = job_status
        task.job_consumed_walltime = job_walltime
        now = timezone.now()
        task.updated = now
        task.save()

        if job_complete:
            __handle_job_success(task, f"Job {task.job_id} completed with status {job_status}" + (f" after {job_walltime}" if job_walltime is not None else ''))
        else:
            # if past due time...
            if now > task.due_time:
                cancel_task(task)
                __handle_failure(task, f"Job {task.job_id} {job_status} (walltime {job_walltime}) is past its due time {str(task.due_time)}")
            else:
                # log the status update
                log_task_orchestrator_status(task, [f"Job {task.job_id} {job_status} (walltime {job_walltime}), refreshing in {refresh_delay}s"])

                # push status to client(s)
                async_to_sync(push_task_channel_event)(task)

                # wait and poll again
                poll_job.s(guid).apply_async(countdown=refresh_delay)
    except:
        self.request.callbacks = None
        __handle_failure(task, f"Failed to poll task {task.guid} job {task.job_id} status: {traceback.format_exc()}")


@app.task(track_started=True, bind=True)
def test_results(self, guid: str):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        self.request.callbacks = None
        return

    try:
        # get logs from agent filesystem
        ssh = get_task_ssh_client(task)
        get_task_remote_logs(task, ssh)

        # get results from agent filesystem, then save them to cache and update the task
        results = list_result_files(task)
        found = [r for r in results if r['exists']]

        redis = RedisClient.get()
        redis.set(f"results/{task.guid}", json.dumps(found))
        task.results_retrieved = True
        task.save()

        # make sure we got the results we expected
        missing = [r for r in results if not r['exists']]
        if len(missing) > 0: message = f"Found {len(found)} results, missing {len(missing)}: {', '.join([m['name'] for m in missing])}"
        else: message = f"Found {len(found)} results"

        # log status update and push it to client(s)
        log_task_orchestrator_status(task, [message])
        async_to_sync(push_task_channel_event)(task)
    except Exception:
        self.request.callbacks = None
        __handle_failure(task, f"Failed to check results for task {task.guid} job {task.job_id}: {traceback.format_exc()}")


@app.task(track_started=True, bind=True)
def test_push(self, guid: str, attempts: int = 0):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        return

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
        self.request.callbacks = None
        __handle_failure(task, f"Failed to test CyVerse transfer for task {task.guid} job {task.job_id}: {traceback.format_exc()}")


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


# misc


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
            if task.job_id is not None:
                poll_job.s(task.guid).apply_async(soft_time_limit=int(settings.TASKS_STEP_TIME_LIMIT_SECONDS))
            else:
                logger.error(f"Couldn't rescue stranded task '{task.guid}' (no job ID)")


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
