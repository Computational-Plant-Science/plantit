import json
import logging
import tempfile
from os import environ
from os.path import join
from pathlib import Path

from asgiref.sync import async_to_sync
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse, FileResponse, HttpResponseBadRequest, \
    HttpResponseServerError
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

import plantit.queries as q
from plantit.sns import SnsClient
from plantit import settings
from plantit.celery_tasks import prep_environment, share_data, submit_jobs, poll_jobs, test_results, test_push, unshare_data, tidy_up
from plantit.task_lifecycle import create_immediate_task, create_delayed_task, create_repeating_task, create_triggered_task, cancel_task
from plantit.task_resources import get_task_ssh_client, push_task_channel_event, log_task_status
from plantit.tasks.models import Task, TaskStatus, DelayedTask, RepeatingTask, TriggeredTask
from plantit.utils.tasks import get_task_orchestrator_log_file_path, \
    get_job_log_file_path, \
    get_task_agent_log_file_path

logger = logging.getLogger(__name__)


# noinspection PyTypeChecker
# @swagger_auto_schema(method='post', auto_schema=None)
# @swagger_auto_schema(methods='get')
@login_required
@swagger_auto_schema(methods=['get', 'post'], auto_schema=None)
@api_view(['GET', 'POST'])
def get_or_create(request):
    if request.method == 'GET':
        return JsonResponse(q.get_tasks(request.user, page=int(request.GET.get('page', 1))))
    elif request.method == 'POST':
        # get the task configuration from the request
        task_config = request.data

        # task type must be configured
        task_type = task_config.get('type', None)
        if task_type is None: return HttpResponseBadRequest()
        else: task_type = task_type.lower()

        # if this is an immediate task, submit it now
        if task_type == 'now':
            # GUIDs for immediate tasks must be set from the client (for now... TODO: is this necessary?)
            if task_config.get('guid', None) is None:
                return HttpResponseBadRequest()

            # create task
            task = create_immediate_task(request.user, task_config)

            # submit Celery task chain
            # (prep_environment.s(task.guid) | share_data.s() | submit_jobs.s() | poll_jobs.s()).apply_async(
            (prep_environment.s(task.guid) | share_data.s() | submit_jobs.s()).apply_async(
                countdown=5,  # TODO: make initial delay configurable
                soft_time_limit=int(settings.TASKS_STEP_TIME_LIMIT_SECONDS))

            created = True
            task_dict = q.task_to_dict(task)

            log_task_status(task, [f"Created task {task.guid} on {task.agent.name}"])
            async_to_sync(push_task_channel_event)(task)

        # otherwise register delayed or repeating task
        elif task_type == 'after':
            task, created = create_delayed_task(request.user, task_config)
            task_dict = q.delayed_task_to_dict(task)
        elif task_type == 'every':
            task, created = create_repeating_task(request.user, task_config)
            task_dict = q.repeating_task_to_dict(task)
        elif task_type == 'watch':
            task, created = create_triggered_task(request.user, task_config)
            task_dict = q.triggered_task_to_dict(task)

        # currently we only support immediate, delayed, and periodic (repeating) tasks
        else:
            raise ValueError(f"Unsupported task type (expected: Now, After, Every, or Watch)")

        return JsonResponse({
            'created': created,
            'task': task_dict
        })


@login_required
@swagger_auto_schema(method='get', auto_schema=None)
@api_view(['GET'])
def get_delayed(request):
    return JsonResponse({'tasks': q.get_delayed_tasks(request.user)})


@login_required
@swagger_auto_schema(method='get', auto_schema=None)
@api_view(['GET'])
def get_repeating(request):
    return JsonResponse({'tasks': q.get_repeating_tasks(request.user)})


@login_required
@swagger_auto_schema(method='get', auto_schema=None)
@api_view(['GET'])
def get_triggered(request):
    return JsonResponse({'tasks': q.get_triggered_tasks(request.user)})


@login_required
@swagger_auto_schema(method='get', auto_schema=None)
@api_view(['GET'])
def get_task(request, guid):
    try:
        task = Task.objects.get(guid=guid)
        owns = request.user.username == task.user.username

        # if the requesting user doesn't own the task and isn't on its
        # associated project team, they're not authorized to access it
        team = [u.username for u in task.project.team.all()]
        if not owns and request.user.username not in team:
            logger.warning(f"Unauthorized access request for task {guid} from user {request.user.username}")
            return HttpResponseNotFound()

        return JsonResponse(q.task_to_dict(task))
    except Task.DoesNotExist:
        return HttpResponseNotFound()


# @login_required
# def get_3d_model(request, guid):
#     body = json.loads(request.body.decode('utf-8'))
#     path = body['path']
#     file = path.rpartition('/')[2]
#     auth = parse_task_auth_options(request.user, body['auth'])
#
#     try:
#         task = Task.objects.get(guid=guid)
#     except:
#         return HttpResponseNotFound()
#
#     ssh = get_task_ssh_client(task, auth)
#     workdir = join(task.agent.workdir, task.workdir)
#
#     with tempfile.NamedTemporaryFile() as temp_file:
#         with ssh:
#             with ssh.client.open_sftp() as sftp:
#                 sftp.chdir(workdir)
#                 sftp.get(file, temp_file.name)
#         return HttpResponse(temp_file, content_type="applications/octet-stream")


@login_required
@swagger_auto_schema(method='get', auto_schema=None)
@api_view(['GET'])
def download_output_file(request, guid):
    try:
        task = Task.objects.get(guid=guid)
        owns = request.user.username == task.user.username

        # if the requesting user doesn't own the task and isn't on its
        # associated project team, they're not authorized to access it
        team = [u.username for u in task.project.team.all()]
        if not owns and request.user.username not in team:
            logger.warning(f"Unauthorized access request for task {guid} from user {request.user.username}")
            return HttpResponseNotFound()
    except Task.DoesNotExist:
        return HttpResponseNotFound()

    body = json.loads(request.body.decode('utf-8'))
    path = body['path']
    ssh = get_task_ssh_client(task)
    workdir = join(task.agent.workdir, task.workdir)

    with ssh:
        with ssh.client.open_sftp() as sftp:
            file_path = join(workdir, path)
            logger.info(f"Downloading {file_path}")

            stdin, stdout, stderr = ssh.client.exec_command('test -e {0} && echo exists'.format(file_path))
            if not stdout.read().decode().strip() == 'exists':
                return HttpResponseNotFound()

            with tempfile.NamedTemporaryFile() as tf:
                sftp.chdir(workdir)
                sftp.get(path, tf.name)
                lower = file_path.lower()
                if lower.endswith('.txt') or lower.endswith('.log') or lower.endswith('.out') or lower.endswith('.err'):
                    return FileResponse(open(tf.name, 'rb'))
                elif lower.endswith('.zip'):
                    response = FileResponse(open(tf.name, 'rb'))
                    # response['Content-Disposition'] = 'attachment; filename={}'.format("%s" % path)
                    return response
                    # return FileResponse(open(tf.name, 'rb'), content_type='application/zip', as_attachment=True)


@login_required
@swagger_auto_schema(method='get', auto_schema=None)
@api_view(['GET'])
def download_task_logs(request, guid):
    try:
        task = Task.objects.get(guid=guid)
        owns = request.user.username == task.user.username

        # if the requesting user doesn't own the task and isn't on its
        # associated project team, they're not authorized to access it
        team = [u.username for u in task.project.team.all()]
        if not owns and request.user.username not in team:
            logger.warning(f"Unauthorized access request for task {guid} from user {request.user.username}")
            return HttpResponseNotFound()
    except Task.DoesNotExist:
        return HttpResponseNotFound()

    log_path = get_task_orchestrator_log_file_path(task)
    return FileResponse(open(log_path, 'rb')) if Path(log_path).is_file() else HttpResponseNotFound()


@login_required
@swagger_auto_schema(method='get', auto_schema=None)
@api_view(['GET'])
def get_task_logs(request, guid):
    try:
        task = Task.objects.get(guid=guid)
        owns = request.user.username == task.user.username

        # if the requesting user doesn't own the task and isn't on its
        # associated project team, they're not authorized to access it
        team = [u.username for u in task.project.team.all()]
        if not owns and request.user.username not in team:
            logger.warning(f"Unauthorized access request for task {guid} from user {request.user.username}")
            return HttpResponseNotFound()
    except Task.DoesNotExist:
        return HttpResponseNotFound()

    log_path = get_task_orchestrator_log_file_path(task)
    if not Path(log_path).is_file(): return HttpResponseNotFound()
    with open(log_path, 'r') as log_file:
        return JsonResponse({'lines': log_file.readlines()})


@login_required
@swagger_auto_schema(method='get', auto_schema=None)
@api_view(['GET'])
def download_scheduler_logs(request, guid):
    try:
        task = Task.objects.get(guid=guid)
        owns = request.user.username == task.user.username

        # if the requesting user doesn't own the task and isn't on its
        # associated project team, they're not authorized to access it
        team = [u.username for u in task.project.team.all()]
        if not owns and request.user.username not in team:
            logger.warning(f"Unauthorized access request for task {guid} from user {request.user.username}")
            return HttpResponseNotFound()
    except Task.DoesNotExist:
        return HttpResponseNotFound()
    with open(get_job_log_file_path(task)) as file:
        return JsonResponse({'lines': file.readlines()})


@login_required
@swagger_auto_schema(method='get', auto_schema=None)
@api_view(['GET'])
def get_scheduler_logs(request, guid):
    try:
        task = Task.objects.get(guid=guid)
        owns = request.user.username == task.user.username

        # if the requesting user doesn't own the task and isn't on its
        # associated project team, they're not authorized to access it
        team = [u.username for u in task.project.team.all()]
        if not owns and request.user.username not in team:
            logger.warning(f"Unauthorized access request for task {guid} from user {request.user.username}")
            return HttpResponseNotFound()
    except Task.DoesNotExist:
        return HttpResponseNotFound()
    with open(get_job_log_file_path(task)) as file:
        return JsonResponse({'lines': file.readlines()})


@login_required
@swagger_auto_schema(method='get', auto_schema=None)
@api_view(['GET'])
def download_agent_logs(request, guid):
    try:
        task = Task.objects.get(guid=guid)
        owns = request.user.username == task.user.username

        # if the requesting user doesn't own the task and isn't on its
        # associated project team, they're not authorized to access it
        team = [u.username for u in task.project.team.all()]
        if not owns and request.user.username not in team:
            logger.warning(f"Unauthorized access request for task {guid} from user {request.user.username}")
            return HttpResponseNotFound()
    except Task.DoesNotExist:
        return HttpResponseNotFound()
    with open(get_task_agent_log_file_path(task)) as file:
        return JsonResponse({'lines': file.readlines()})


@login_required
@swagger_auto_schema(method='get', auto_schema=None)
@api_view(['GET'])
def get_agent_logs(request, guid):
    try:
        task = Task.objects.get(guid=guid)
        owns = request.user.username == task.user.username

        # if the requesting user doesn't own the task and isn't on its
        # associated project team, they're not authorized to access it
        team = [u.username for u in task.project.team.all()]
        if not owns and request.user.username not in team:
            logger.warning(f"Unauthorized access request for task {guid} from user {request.user.username}")
            return HttpResponseNotFound()
    except Task.DoesNotExist:
        return HttpResponseNotFound()
    with open(get_task_agent_log_file_path(task)) as file:
        return JsonResponse({'lines': file.readlines()})


def __cancel(task: Task):
    cancel_task(task)
    log_task_status(task, [f"Cancelled user {task.user.username}'s task {task.guid}"])
    push_task_channel_event(task)


@login_required
@swagger_auto_schema(method='post', auto_schema=None)
@api_view(['POST'])
def cancel(request, guid):
    try:
        task = Task.objects.get(user=request.user, guid=guid)
    except MultipleObjectsReturned:
        tasks = list(Task.objects.filter(user=request.user, guid=guid))
        logger.warning(f"Found {len(tasks)} tasks for user {request.user.username} matching GUID {guid}")
        for task in tasks: __cancel(task)
        return HttpResponseServerError()
    except:
        return HttpResponseNotFound()

    if task.is_complete:
        return HttpResponse(f"User {request.user.username}'s task {guid} already completed")

    __cancel(task)
    return JsonResponse(q.task_to_dict(task))


# TODO switch to post
@login_required
@swagger_auto_schema(method='get', auto_schema=None)
@api_view(['GET'])
def unschedule_delayed(request, guid):
    try:
        task = DelayedTask.objects.get(user=request.user, name=guid)
    except:
        return HttpResponseNotFound()
    task.delete()

    # TODO paginate
    return JsonResponse({'tasks': [q.delayed_task_to_dict(task) for task in
                                   DelayedTask.objects.filter(user=request.user, enabled=True)]})


# TODO switch to post
@login_required
@swagger_auto_schema(method='get', auto_schema=None)
@api_view(['GET'])
def unschedule_repeating(request, guid):
    try:
        task = RepeatingTask.objects.get(user=request.user, name=guid)
    except:
        return HttpResponseNotFound()
    task.delete()

    # TODO paginate
    return JsonResponse({'tasks': [q.repeating_task_to_dict(task) for task in
                                   RepeatingTask.objects.filter(user=request.user, enabled=True)]})


# TODO switch to post
@login_required
@swagger_auto_schema(method='get', auto_schema=None)
@api_view(['GET'])
def unschedule_triggered(request, guid):
    try:
        task = TriggeredTask.objects.get(user=request.user, name=guid)
    except:
        return HttpResponseNotFound()
    task.delete()

    # TODO paginate
    return JsonResponse({'tasks': [q.triggered_task_to_dict(task) for task in
                                   TriggeredTask.objects.filter(user=request.user, enabled=True)]})


@login_required
@swagger_auto_schema(method='get', auto_schema=None)
@api_view(['GET'])
def exists(request, guid):
    try:
        task = Task.objects.get(guid=guid)
        owns = request.user.username == task.user.username

        # if the requesting user doesn't own the task and isn't on its
        # associated project team, they're not authorized to access it
        team = [u.username for u in task.project.team.all()]
        if not owns and request.user.username not in team:
            logger.warning(f"Unauthorized access request for task {guid} from user {request.user.username}")
            return HttpResponseNotFound()
        return JsonResponse({'exists': True})
    except Task.DoesNotExist:
        return JsonResponse({'exists': False})


@login_required
@swagger_auto_schema(method='get', auto_schema=None)
@api_view(['GET'])
def search(request, owner, workflow_name, page):
    try:
        user = User.objects.get(username=owner)

        # TODO automatic pagination, no need for manual
        start = int(page) * 20
        count = start + 20
        tasks = Task.objects.filter(user=user, workflow_name=workflow_name).order_by('-created')[start:(start + count)]
        return JsonResponse([q.task_to_dict(t) for t in tasks], safe=False)
    except:
        return HttpResponseNotFound()


@login_required
@swagger_auto_schema(method='get', auto_schema=None)
@api_view(['GET'])
def search_delayed(request, owner, workflow_name):
    user = User.objects.get(username=owner)
    try:
        tasks = DelayedTask.objects.filter(user=user)
    except:
        return HttpResponseNotFound()

    # TODO paginate
    tasks = [t for t in tasks if t.workflow_name == workflow_name]
    return JsonResponse([q.delayed_task_to_dict(t) for t in tasks], safe=False)


@login_required
@swagger_auto_schema(method='get', auto_schema=None)
@api_view(['GET'])
def search_repeating(request, owner, workflow_name):
    user = User.objects.get(username=owner)
    try:
        tasks = RepeatingTask.objects.filter(user=user)
    except:
        return HttpResponseNotFound()

    # TODO paginate
    tasks = [t for t in tasks if t.workflow_name == workflow_name]
    return JsonResponse([q.repeating_task_to_dict(t) for t in tasks], safe=False)


@login_required
@swagger_auto_schema(method='get', auto_schema=None)
@api_view(['GET'])
def search_triggered(request, owner, workflow_name):
    user = User.objects.get(username=owner)
    try:
        tasks = TriggeredTask.objects.filter(user=user)
    except:
        return HttpResponseNotFound()

    # TODO paginate
    tasks = [t for t in tasks if t.workflow_name == workflow_name]
    return JsonResponse([q.triggered_task_to_dict(t) for t in tasks], safe=False)


@api_view(['POST'])
def complete(request, guid):
    try:
        task = Task.objects.get(guid=guid)
    except MultipleObjectsReturned:
        tasks = list(Task.objects.filter(user=request.user, guid=guid))
        logger.warning(f"Found {len(tasks)} tasks for user {request.user.username} matching GUID {guid}")
        for task in tasks:
            complete_task(task)
        return HttpResponseServerError()
    except Exception as e:
        logger.error(e)
        return HttpResponseNotFound()

    if task.is_complete:
        return HttpResponse(f"User {request.user.username}'s task {guid} already completed")

    # success = request.data.get('success', None)
    # if success is None:
    #     return HttpResponseBadRequest()

    # complete_task(task, bool(success))
    complete_task(task, True)
    return JsonResponse(q.task_to_dict(task))


def complete_task(task: Task, success: bool):
    message = f"User {task.user.username}'s task {task.guid} {'completed successfully' if success else 'failed'}"
    if success:
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
            SnsClient.get().publish_message(task.user.profile.push_notification_topic_arn, f"plantit task {task.guid}", message, {})

        # submit the outbound data transfer job
        (test_results.s(task.guid) | test_push.s() | unshare_data.s()).apply_async(soft_time_limit=int(settings.TASKS_STEP_TIME_LIMIT_SECONDS))
        tidy_up.s(task.guid).apply_async(countdown=int(environ.get('TASKS_CLEANUP_MINUTES')) * 60)
    else:
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
