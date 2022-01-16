import json
import logging
import subprocess
import tempfile
from os.path import join
from pathlib import Path
from zipfile import ZipFile

from asgiref.sync import sync_to_async, async_to_sync
from celery.result import AsyncResult
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse, FileResponse, HttpResponseBadRequest, StreamingHttpResponse, \
    HttpResponseForbidden
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from paramiko.message import Message

from plantit import settings
from plantit.redis import RedisClient
from plantit.agents.models import Agent, AgentExecutor
from plantit.celery_tasks import prepare_task_environment, submit_task, poll_task_status, list_task_results, check_task_cyverse_transfer, cleanup_task
from plantit.ssh import execute_command
from plantit.tasks.models import Task, DelayedTask, RepeatingTask, TaskStatus
from plantit.utils import task_to_dict, create_task, parse_task_auth_options, get_task_ssh_client, get_task_orchestrator_log_file_path, create_immediate_task, create_delayed_task, create_repeating_task, \
    log_task_orchestrator_status, \
    push_task_event, cancel_task, delayed_task_to_dict, repeating_task_to_dict, parse_time_limit_seconds, \
    get_task_scheduler_log_file_path, get_task_agent_log_file_path, \
    get_included_by_name, get_included_by_pattern

logger = logging.getLogger(__name__)


# noinspection PyTypeChecker
@login_required
@swagger_auto_schema(method='post', auto_schema=None)
def get_all_or_create(request):
    if request.method == 'GET':
        tasks = Task.objects.filter(user=request.user)
        paginator = Paginator(tasks, 20)
        page = paginator.get_page(int(request.GET.get('page', 1)))

        return JsonResponse({
            'previous_page': page.has_previous() and page.previous_page_number() or None,
            'next_page': page.has_next() and page.next_page_number() or None,
            'tasks': [task_to_dict(task) for task in list(page)]
        })
    elif request.method == 'POST':
        workflow = json.loads(request.body.decode('utf-8'))
        if workflow['type'] == 'Now':
            if workflow['config'].get('task_guid', None) is None: return HttpResponseBadRequest()

            # create task and submit task chain immediately
            task = create_immediate_task(request.user, workflow)
            task_time_limit = parse_time_limit_seconds(task.workflow['config']['time'])
            step_time_limit = int(settings.TASKS_STEP_TIME_LIMIT_SECONDS)
            auth = parse_task_auth_options(task, task.workflow['auth'])
            (prepare_task_environment.s(task.guid, auth) | \
             submit_task.s(auth) | \
             poll_task_status.s(auth)).apply_async(
                soft_time_limit=task_time_limit if task.agent.executor == AgentExecutor.LOCAL else step_time_limit,
                priority=1)

            return JsonResponse(task_to_dict(task))
        elif workflow['type'] == 'After':
            task, created = create_delayed_task(request.user, workflow)
            return JsonResponse({
                'created': created,
                'task': delayed_task_to_dict(task)
            })
        elif workflow['type'] == 'Every':
            task,created = create_repeating_task(request.user, workflow)
            return JsonResponse({
                'created': created,
                'task': repeating_task_to_dict(task)
            })
        else:
            raise ValueError(f"Unsupported task type (expected: Now, After, or Every)")


@login_required
def get_delayed(request):
    return JsonResponse({'tasks': [delayed_task_to_dict(task) for task in DelayedTask.objects.filter(user=request.user, enabled=True)]})


@login_required
def get_repeating(request):
    return JsonResponse({'tasks': [repeating_task_to_dict(task) for task in RepeatingTask.objects.filter(user=request.user, enabled=True)]})


@login_required
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

        return JsonResponse(task_to_dict(task))
    except Task.DoesNotExist: return HttpResponseNotFound()


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


# noinspection PyTypeChecker
@login_required
@swagger_auto_schema(method='get', auto_schema=None)
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
    except Task.DoesNotExist: return HttpResponseNotFound()

    body = json.loads(request.body.decode('utf-8'))
    path = body['path']
    auth = parse_task_auth_options(task, body['auth'])
    ssh = get_task_ssh_client(task, auth)
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


# noinspection PyTypeChecker
@login_required
@swagger_auto_schema(method='get', auto_schema=None)
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
    except Task.DoesNotExist: return HttpResponseNotFound()

    log_path = get_task_orchestrator_log_file_path(task)
    return FileResponse(open(log_path, 'rb')) if Path(log_path).is_file() else HttpResponseNotFound()


@login_required
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
    except Task.DoesNotExist: return HttpResponseNotFound()

    log_path = get_task_orchestrator_log_file_path(task)
    if not Path(log_path).is_file(): return HttpResponseNotFound()
    with open(log_path, 'r') as log_file: return JsonResponse({'lines': log_file.readlines()})


# noinspection PyTypeChecker
@login_required
@swagger_auto_schema(method='get', auto_schema=None)
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
    except Task.DoesNotExist: return HttpResponseNotFound()
    with open(get_task_scheduler_log_file_path(task)) as file: return JsonResponse({'lines': file.readlines()})


@login_required
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
    except Task.DoesNotExist: return HttpResponseNotFound()
    with open(get_task_scheduler_log_file_path(task)) as file: return JsonResponse({'lines': file.readlines()})


# noinspection PyTypeChecker
@login_required
@swagger_auto_schema(method='get', auto_schema=None)
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
    except Task.DoesNotExist: return HttpResponseNotFound()
    with open(get_task_agent_log_file_path(task)) as file: return JsonResponse({'lines': file.readlines()})


@login_required
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
    except Task.DoesNotExist: return HttpResponseNotFound()
    with open(get_task_agent_log_file_path(task)) as file: return JsonResponse({'lines': file.readlines()})


# @login_required
# def get_file_text(request, owner, name):
#     file = request.GET.get('path')
#     try:
#         user = User.objects.get(username=owner)
#         task = Task.objects.get(user=user, name=name)
#     except Task.DoesNotExist:
#         return HttpResponseNotFound()
#
#     body = json.loads(request.body.decode('utf-8'))
#     auth = parse_task_auth_options(task, body['auth'])
#
#     ssh = get_task_ssh_client(task, auth)
#     workdir = join(task.agent.workdir, task.workdir)
#
#     with ssh:
#         with ssh.client.open_sftp() as sftp:
#             path = join(workdir, file)
#             stdin, stdout, stderr = ssh.client.exec_command(
#                 'test -e {0} && echo exists'.format(path))
#             errs = stderr.read()
#             if errs:
#                 raise Exception(f"Failed to check existence of {file}: {errs}")
#             if not stdout.read().decode().strip() == 'exists':
#                 return HttpResponseNotFound()
#
#             stdin, stdout, stderr = ssh.client.exec_command(f"cat {path}")
#             return JsonResponse({'text': stdout.readlines()})


@login_required
def cancel(request, guid):
    try:
        task = Task.objects.get(user=request.user, guid=guid)
    except:
        return HttpResponseNotFound()

    if task.is_complete:
        return HttpResponse(f"User {request.user.username}'s task {guid} already completed")

    if task.agent.executor == AgentExecutor.LOCAL and task.celery_task_id is not None:
        AsyncResult(task.celery_task_id).revoke()  # cancel the Celery task
    else:
        auth = parse_task_auth_options(task, json.loads(request.body.decode('utf-8'))['auth'])
        cancel_task(task, auth)

    now = timezone.now()
    task.status = TaskStatus.CANCELED
    task.updated = now
    task.completed = now
    task.save()

    msg = f"Cancelled user {request.user.username}'s task {guid}"
    log_task_orchestrator_status(task, [msg])
    push_task_event(task)
    return JsonResponse({'canceled': True})


# @login_required
# def delete(request, owner, name):
#     try:
#         user = User.objects.get(username=owner)
#         task = Task.objects.get(user=user, guid=name)
#     except:
#         return HttpResponseNotFound()
#
#     task.delete()
#     tasks = list(Task.objects.filter(user=user))
#
#     return JsonResponse({'tasks': [task_to_dict(t) for t in tasks]})


@login_required
def unschedule_delayed(request, guid):
    try: task = DelayedTask.objects.get(user=request.user, name=guid)
    except: return HttpResponseNotFound()
    task.delete()
    return JsonResponse({'tasks': [delayed_task_to_dict(task) for task in DelayedTask.objects.filter(user=request.user, enabled=True)]})


@login_required
def unschedule_repeating(request, guid):
    try: task = RepeatingTask.objects.get(user=request.user, name=guid)
    except: return HttpResponseNotFound()
    task.delete()
    return JsonResponse({'tasks': [repeating_task_to_dict(task) for task in RepeatingTask.objects.filter(user=request.user, enabled=True)]})


@login_required
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
    except Task.DoesNotExist: return JsonResponse({'exists': False})


@login_required
def search(request, owner, workflow_name, page):
    try:
        user = User.objects.get(username=owner)
        start = int(page) * 20
        count = start + 20
        tasks = Task.objects.filter(user=user, workflow_name=workflow_name).order_by('-created')[start:(start + count)]
        return JsonResponse([task_to_dict(t) for t in tasks], safe=False)
    except:
        return HttpResponseNotFound()


@login_required
def search_delayed(request, owner, workflow_name):
    user = User.objects.get(username=owner)
    try:
        tasks = DelayedTask.objects.filter(user=user)
    except:
        return HttpResponseNotFound()

    tasks = [t for t in tasks if t.workflow_name == workflow_name]
    return JsonResponse([delayed_task_to_dict(t) for t in tasks], safe=False)


@login_required
def search_repeating(request, owner, workflow_name):
    user = User.objects.get(username=owner)
    try:
        tasks = RepeatingTask.objects.filter(user=user)
    except:
        return HttpResponseNotFound()

    tasks = [t for t in tasks if t.workflow_name == workflow_name]
    return JsonResponse([repeating_task_to_dict(t) for t in tasks], safe=False)
