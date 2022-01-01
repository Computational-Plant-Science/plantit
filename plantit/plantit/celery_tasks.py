import json
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

import plantit.terrain as terrain
from plantit import settings
from plantit.agents.models import AgentExecutor, Agent, AgentAuthentication
from plantit.celery import app
from plantit.github import get_repo
from plantit.redis import RedisClient
from plantit.sns import SnsClient
from plantit.ssh import execute_command
from plantit.tasks.models import Task, TaskStatus
from plantit.utils import get_workflow, log_task_orchestrator_status, push_task_event, get_task_ssh_client, configure_local_task_environment, execute_local_task, \
    submit_jobqueue_task, parse_time_limit_seconds, parse_task_auth_options, create_now_task, \
    get_jobqueue_task_job_status, get_jobqueue_task_job_walltime, get_task_remote_logs, get_task_result_files, \
    refresh_user_workflow_cache, refresh_org_workflow_cache, refresh_online_user_orgs_workflow_cache, calculate_user_statistics, repopulate_institutions_cache, \
    configure_jobqueue_task_environment, check_logs_for_progress, is_healthy, refresh_user_cyverse_tokens, refresh_online_users_workflow_cache, get_users_timeseries, get_tasks_timeseries, get_tasks_running_timeseries

logger = get_task_logger(__name__)


# Task lifecycle:
#   prep environment
#   submit executable/run script
#   poll status until complete
#   check results
#   check CyVerse transfer
#   clean up


@app.task(track_started=True)
def create_and_submit(username, workflow):
    try:
        user = User.objects.get(username=username)
    except:
        logger.error(traceback.format_exc())
        return

    task = create_now_task(user, workflow)
    task_time_limit = parse_time_limit_seconds(task.workflow['config']['time'])
    step_time_limit = int(settings.TASKS_STEP_TIME_LIMIT_SECONDS)
    auth = parse_task_auth_options(task, task.workflow['auth'])
    (prepare_task_environment.s(task.guid, auth) | \
     submit_task.s(auth) | \
     poll_task_status.s(auth)).apply_async(
        soft_time_limit=task_time_limit if task.agent.executor == AgentExecutor.LOCAL else step_time_limit,
        priority=1)


@app.task(track_started=True, bind=True)
def prepare_task_environment(self, guid: str, auth: dict):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        return

    try:
        print(auth)
        ssh = get_task_ssh_client(task, auth)
        with ssh:
            log_task_orchestrator_status(task, [f"Preparing environment for {task.user.username}'s task {task.name} on {task.agent.name}"])
            async_to_sync(push_task_event)(task)

            local = task.agent.executor == AgentExecutor.LOCAL
            if local: configure_local_task_environment(task, ssh)
            else: configure_jobqueue_task_environment(task, ssh, auth)
        return guid
    except Exception:
        task.status = TaskStatus.FAILURE
        now = timezone.now()
        task.updated = now
        task.completed = now
        task.save()

        error = traceback.format_exc()
        log_task_orchestrator_status(task, [f"Failed with error: {error}"])
        logger.error(f"Failed to prepare environment for {task.user.username}'s task {task.name} on {task.agent.name}: {error}")
        async_to_sync(push_task_event)(task)
        self.request.callbacks = None # stop the task chain


@app.task(track_started=True, bind=True)
def submit_task(self, guid: str, auth: dict):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        self.request.callbacks = None  # stop the task chain
        return

    local = task.agent.executor == AgentExecutor.LOCAL
    task.status = TaskStatus.RUNNING
    task.celery_task_id = submit_task.request.id  # set the Celery task's ID so user can cancel
    task.save()

    try:
        ssh = get_task_ssh_client(task, auth)

        with ssh:
            if local:
                log_task_orchestrator_status(task, [f"Invoking executable"])
                async_to_sync(push_task_event)(task)

                execute_local_task(task, ssh)
                task.status = TaskStatus.SUCCESS
                task.save()

                message = f"Task {task.name} (GUID: {task.guid}) succeeded"
                log_task_orchestrator_status(task, [message])
                async_to_sync(push_task_event)(task)

                if task.user.profile.push_notification_status == 'enabled':
                    SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT task {task.guid}", message, {})

                check_logs_for_progress(task)
            else:
                log_task_orchestrator_status(task, [f"Submitting job script"])
                async_to_sync(push_task_event)(task)

                job_id = submit_jobqueue_task(task, ssh)

                log_task_orchestrator_status(task, [f"Scheduled job {job_id}"])
                async_to_sync(push_task_event)(task)

            return guid
    except Exception:
        task.status = TaskStatus.FAILURE
        now = timezone.now()
        task.updated = now
        task.completed = now
        task.save()

        error = traceback.format_exc()
        log_task_orchestrator_status(task, [f"Failed with error: {error}"])
        logger.error(f"Failed to {'run' if local else 'submit'} {task.user.username}'s task {task.name} on {task.agent.name}: {error}")
        async_to_sync(push_task_event)(task)
        self.request.callbacks = None  # stop the task chain


@app.task(bind=True)
def poll_task_status(self, guid: str, auth: dict):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        self.request.callbacks = None  # stop the task chain
        return

    refresh_delay = int(environ.get('TASKS_REFRESH_SECONDS'))
    cleanup_delay = int(environ.get('TASKS_CLEANUP_MINUTES')) * 60
    logger.info(f"Checking {task.agent.name} scheduler status for run {guid} (SLURM job {task.job_id})")

    # if the job already failed, schedule cleanup
    if task.job_status == 'FAILURE':
        task.status = TaskStatus.FAILURE
        final_message = f"Job {task.job_id} failed"
        log_task_orchestrator_status(task, [final_message])
        async_to_sync(push_task_event)(task)
        cleanup_task.s(guid, auth).apply_async(countdown=cleanup_delay, priority=2)
        task.cleanup_time = timezone.now() + timedelta(seconds=cleanup_delay)
        task.save()

        if task.user.profile.push_notification_status == 'enabled':
            SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT task {task.guid}", final_message, {})

        return guid

    # if the task already completed
    local = task.agent.executor == AgentExecutor.LOCAL
    if local:
        if task.status == TaskStatus.SUCCESS:
            ssh = get_task_ssh_client(task, auth)
            get_task_remote_logs(task, ssh)

            check_logs_for_progress(task)

            list_task_results.s(guid, auth).apply_async()
            final_message = f"{task.agent.executor} task {task.guid} completed"
            log_task_orchestrator_status(task, [final_message])
            async_to_sync(push_task_event)(task)

            if task.user.profile.push_notification_status == 'enabled':
                SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT task {task.guid}", final_message, {})

            return guid
        if task.status == TaskStatus.FAILURE:
            self.request.callbacks = None  # stop the task chain
            return

    # otherwise poll the scheduler for its status
    try:
        check_logs_for_progress(task)

        job_status = get_jobqueue_task_job_status(task, auth)
        job_walltime = get_jobqueue_task_job_walltime(task, auth)
        task.job_status = job_status
        task.job_consumed_walltime = job_walltime

        now = timezone.now()
        task.updated = now
        task.save()

        ssh = get_task_ssh_client(task, auth)
        get_task_remote_logs(task, ssh)

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
            list_task_results.s(guid, auth).apply_async()
            final_message = f"Job {task.job_id} {job_status}" + (f" after {job_walltime}" if job_walltime is not None else '')
            log_task_orchestrator_status(task, [final_message])
            async_to_sync(push_task_event)(task)

            if task.user.profile.push_notification_status == 'enabled':
                SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT task {task.guid}", final_message, {})

            return guid
        else:
            log_task_orchestrator_status(task, [f"Job {task.job_id} {job_status}, walltime {job_walltime}"])
            async_to_sync(push_task_event)(task)
            poll_task_status.s(guid, auth).apply_async(countdown=refresh_delay)
    except StopIteration as e:
        if not (task.job_status == 'COMPLETED' or task.job_status == 'COMPLETING'):
            now = timezone.now()
            task.updated = now
            task.save()

            retry_seconds = 10
            log_task_orchestrator_status(task, [f"Job {task.job_id} not found, retrying in {retry_seconds} seconds"])
            async_to_sync(push_task_event)(task)
            poll_task_status.s(guid, auth).apply_async(countdown=retry_seconds)
            return
        else:
            final_message = f"Job {task.job_id} succeeded"
            log_task_orchestrator_status(task, [final_message])
            async_to_sync(push_task_event)(task)
            cleanup_task.s(guid, auth).apply_async(countdown=cleanup_delay, priority=2)
            task.cleanup_time = timezone.now() + timedelta(seconds=cleanup_delay)
            task.save()

            if task.user.profile.push_notification_status == 'enabled':
                SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT task {task.guid}", final_message, {})

            return guid
    except:
        task.status = TaskStatus.FAILURE
        now = timezone.now()
        task.updated = now
        task.completed = now
        task.save()

        final_message = f"Job {task.job_id} encountered unexpected error: {traceback.format_exc()}"
        log_task_orchestrator_status(task, [final_message])
        async_to_sync(push_task_event)(task)
        cleanup_task.s(guid, auth).apply_async(countdown=cleanup_delay, priority=2)
        task.cleanup_time = timezone.now() + timedelta(seconds=cleanup_delay)
        task.save()

        if task.user.profile.push_notification_status == 'enabled':
            SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"PlantIT task {task.guid}", final_message, {})

        self.request.callbacks = None  # stop the task chain


@app.task(bind=True)
def list_task_results(self, guid: str, auth: dict):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        self.request.callbacks = None  # stop the task chain
        return

    redis = RedisClient.get()
    ssh = get_task_ssh_client(task, auth)
    workflow = redis.get(f"workflows/{task.workflow_owner}/{task.workflow_name}/{task.workflow_branch}")

    if workflow is None:
        workflow = async_to_sync(get_workflow)(
            task.workflow_owner,
            task.workflow_name,
            task.workflow_branch,
            task.user.profile.github_token,
            task.user.profile.cyverse_access_token)['config']
    else:
        workflow = json.loads(workflow)['config']

    log_task_orchestrator_status(task, [f"Retrieving logs"])
    async_to_sync(push_task_event)(task)
    get_task_remote_logs(task, ssh)

    log_task_orchestrator_status(task, [f"Retrieving results"])
    async_to_sync(push_task_event)(task)
    expected = get_task_result_files(task, workflow, auth)
    found = [e for e in expected if e['exists']]
    redis.set(f"results/{task.guid}", json.dumps(found))
    task.results_retrieved = True
    task.save()

    log_task_orchestrator_status(task, [f"Expected {len(expected)} result(s), found {len(found)}, verifying data was transferred to CyVerse"])
    async_to_sync(push_task_event)(task)
    check_task_cyverse_transfer.s(guid=guid, auth=auth).apply_async()

    return guid


@app.task(bind=True)
def check_task_cyverse_transfer(self, guid: str, auth: dict, iteration: int = 0):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        self.request.callbacks = None  # stop the task chain
        return

    path = task.workflow['config']['output']['to']
    actual = [file.rpartition('/')[2] for file in terrain.list_dir(path, task.user.profile.cyverse_access_token)]
    expected = [file['name'] for file in json.loads(RedisClient.get().get(f"results/{task.guid}"))]

    if not set(expected).issubset(set(actual)):
        logger.warning(f"Expected {len(expected)} results but found {len(actual)}")
        if iteration < 5:
            logger.warning(f"Checking again in 30 seconds (iteration {iteration})")
            check_task_cyverse_transfer.s(guid, auth, iteration + 1).apply_async(countdown=30)
    else:
        msg = f"Transfer to CyVerse directory {path} completed"
        logger.info(msg)
        task.transferred = True
        task.results_transferred = len(expected)
        task.transfer_path = path
        task.save()

        log_task_orchestrator_status(task, [msg])
        async_to_sync(push_task_event)(task)

    cleanup_delay = int(environ.get('TASKS_CLEANUP_MINUTES')) * 60
    cleanup_task.s(guid, auth).apply_async(priority=2, countdown=cleanup_delay)

    return guid


@app.task(bind=True)
def cleanup_task(self, guid: str, auth: dict):
    try:
        task = Task.objects.get(guid=guid)
    except:
        logger.warning(f"Could not find task with GUID {guid} (might have been deleted?)")
        self.request.callbacks = None  # stop the task chain
        return

    # logger.info(f"Cleaning up task with GUID {guid} local working directory {task.agent.workdir}")
    # remove_task_orchestration_logs(task)

    logger.info(f"Cleaning up task with GUID {guid} remote working directory {task.agent.workdir}")
    command = f"rm -rf {join(task.agent.workdir, task.workdir)}"
    ssh = get_task_ssh_client(task, auth)
    with ssh:
        for line in execute_command(ssh=ssh, precommand=task.agent.pre_commands, command=command, directory=task.agent.workdir, allow_stderr=True):
            logger.info(f"[{task.agent.name}] {line}")

    task.cleaned_up = True
    task.save()

    log_task_orchestrator_status(task, [f"Cleaned up task {task.guid}"])
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


@app.task()
def refresh_all_users_stats():
    users = User.objects.all()
    for user in users:
        logger.info(f"Computing statistics for {user.username}")
        stats = async_to_sync(calculate_user_statistics)(user)
        redis = RedisClient.get()
        redis.set(f"stats/{user.username}", json.dumps(stats))
        redis.set(f"stats_updated/{user.username}", datetime.now().timestamp())

    logger.info(f"Computing aggregate statistics for {user.username}")
    users_series = get_users_timeseries()
    tasks_series = get_tasks_timeseries()
    tasks_running_series = get_tasks_running_timeseries(600)

    now = datetime.now()
    redis = RedisClient.get()
    redis.set(f"users_timeseries", json.dumps(users_series))
    redis.set(f"users_timeseries_updated", now.timestamp())
    redis.set(f"tasks_timeseries", json.dumps(tasks_series))
    redis.set(f"tasks_timeseries_updated", now.timestamp())
    redis.set(f"tasks_running", json.dumps(tasks_running_series))
    redis.set(f"tasks_running_updated", now.timestamp())


@app.task()
def refresh_user_stats(username: str):
    try:
        user = User.objects.get(username=username)
    except:
        logger.warning(f"User {username} not found: {traceback.format_exc()}")
        return

    logger.info(f"Aggregating statistics for {user.username}")
    stats = async_to_sync(calculate_user_statistics)(user)
    redis = RedisClient.get()
    redis.set(f"stats/{user.username}", json.dumps(stats))
    redis.set(f"stats_updated/{user.username}", datetime.now().timestamp())


@app.task()
def refresh_user_workflows(owner: str):
    async_to_sync(refresh_user_workflow_cache)(owner)


@app.task()
def refresh_all_workflows():
    async_to_sync(refresh_online_users_workflow_cache)()
    async_to_sync(refresh_online_user_orgs_workflow_cache)()


@app.task()
def refresh_user_institutions():
    repopulate_institutions_cache()


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
        healthy, output = is_healthy(agent, {'username': agent.user.username, 'port': agent.port})
        agent.is_healthy = healthy
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


@app.task()
def stranded_task_sweep():
    running = Task.objects.filter(status=TaskStatus.RUNNING)
    for task in running:
        now = timezone.now()
        period = int(environ.get('TASKS_REFRESH_SECONDS'))
        # if the task is still running and hasn't been updated in the last 2 refresh cycles, it might be stranded
        if (now - task.updated).total_seconds() > (2 * period):
            logger.warning(f"Found possibly stranded task: {task.guid}")
            # TODO for now, flag these in the UI for the user to debug manually
            # it's a bad idea to persist auth info anywhere beyond the task invocation chain, so we can't poll agent status


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

        response = requests.get('https://de.cyverse.org/terrain/token/cas', auth=(cyverse_username, cyverse_password)).json()
        TerrainToken.__token = response['access_token']

        return TerrainToken.__token


# see https://stackoverflow.com/a/41119054/6514033
# `@app.on_after_finalize.connect` is necessary for some reason instead of `@app.on_after_configure.connect`
@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    logger.info("Scheduling periodic tasks")

    # refresh CyVerse auth tokens for all users with running tasks (in case outputs need to get pushed on completion)
    sender.add_periodic_task(int(settings.CYVERSE_TOKEN_REFRESH_MINUTES) * 60, refresh_all_user_cyverse_tokens.s(), name='refresh CyVerse tokens for users with running tasks', priority=1)

    # refresh user institution geocoding info
    sender.add_periodic_task(int(settings.MAPBOX_FEATURE_REFRESH_MINUTES) * 60, refresh_user_institutions.s(), name='refresh user institutions', priority=2)

    # aggregate usage stats for each user
    sender.add_periodic_task(int(settings.USERS_STATS_REFRESH_MINUTES) * 60, refresh_all_users_stats.s(), name='refresh user statistics', priority=2)

    # agent healthchecks
    # TODO reenable with better scheduling strategy
    # sender.add_periodic_task(int(settings.AGENTS_HEALTHCHECKS_MINUTES) * 60, agents_healthchecks.s(), name='check agent connections', priority=1)

    # refresh workflow cache
    sender.add_periodic_task(int(settings.WORKFLOWS_REFRESH_MINUTES) * 60, refresh_all_workflows.s(), name='refresh workflows cache', priority=2)

    # stranded task sweeps
    sender.add_periodic_task(int(settings.TASKS_REFRESH_SECONDS), stranded_task_sweep, name='check for stranded tasks', priority=2)
