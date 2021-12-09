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
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse, FileResponse, HttpResponseBadRequest, StreamingHttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from paramiko.message import Message

from plantit import settings
from plantit.redis import RedisClient
from plantit.agents.models import Agent, AgentExecutor
from plantit.celery_tasks import prepare_task_environment, submit_task, poll_task_status, list_task_results, check_task_cyverse_transfer, cleanup_task
from plantit.ssh import execute_command
from plantit.tasks.models import Task, DelayedTask, RepeatingTask, TaskStatus
from plantit.utils import task_to_dict, create_task, parse_task_auth_options, get_task_ssh_client, get_task_orchestrator_log_file_path, \
    log_task_orchestrator_status, \
    push_task_event, cancel_task, delayed_task_to_dict, repeating_task_to_dict, parse_time_limit_seconds, \
    get_task_scheduler_log_file_path, get_task_agent_log_file_path, \
    get_included_by_name, get_included_by_pattern

logger = logging.getLogger(__name__)


@login_required
def get_all_or_create(request):
    user = request.user
    workflow = json.loads(request.body.decode('utf-8'))

    if request.method == 'GET':
        tasks = Task.objects.all()
        return JsonResponse({'tasks': [task_to_dict(sub) for sub in tasks]})
    elif request.method == 'POST':
        if workflow['type'] == 'Now':
            repo_owner = workflow['repo']['owner']['login']
            repo_name = workflow['repo']['name']
            repo_branch = workflow['branch']['name']

            redis = RedisClient.get()
            last_config = workflow.copy()
            del last_config['auth']
            last_config['timestamp'] = timezone.now().isoformat()
            redis.set(f"workflow_configs/{request.user.username}/{repo_owner}/{repo_name}/{repo_branch}", json.dumps(last_config))

            config = workflow['config']
            branch = workflow['branch']
            task_name = config.get('task_name', None)
            task_guid = config.get('task_guid', None)

            if task_guid is None: return HttpResponseBadRequest()

            task_time_limit = parse_time_limit_seconds(workflow['config']['time'])
            step_time_limit = int(settings.TASKS_STEP_TIME_LIMIT_SECONDS)
            agent = Agent.objects.get(name=config['agent']['name'])
            auth = parse_task_auth_options(workflow['auth'])
            task = create_task(
                username=user.username,
                agent_name=agent.name,
                workflow=workflow,
                branch=branch,
                name=task_name if task_name is not None and task_name != '' else task_guid,
                guid=task_guid,
                investigation=workflow['miappe']['project']['title'] if workflow['miappe']['project'] is not None else None,
                study=workflow['miappe']['study']['title'] if workflow['miappe']['study'] is not None else None)

            (prepare_task_environment.s(task.guid, auth) |\
             submit_task.s(auth) |\
             poll_task_status.s(auth)).apply_async(
                soft_time_limit=task_time_limit if agent.executor == AgentExecutor.LOCAL else step_time_limit,
                priority=1)

            return JsonResponse(task_to_dict(task))

        # TODO refactor delayed/repeating task logic, maybe move to `create_task`
        # elif workflow['type'] == 'After':
        #     eta, seconds = parse_task_eta(workflow)
        #     schedule, _ = IntervalSchedule.objects.get_or_create(every=seconds, period=IntervalSchedule.SECONDS)
        #     task, created = DelayedTask.objects.get_or_create(
        #         user=user,
        #         interval=schedule,
        #         agent=agent,
        #         eta=eta,
        #         one_off=True,
        #         workflow_owner=workflow['repo']['owner']['login'],
        #         workflow_name=workflow['repo']['name'],
        #         name=f"User {user.username} workflow {workflow['repo']['name']} agent {agent.name} {schedule} once",
        #         task='plantit.celery_tasks.create_and_submit_task',
        #         args=json.dumps([user.username, agent.name, workflow]))
        #     return JsonResponse({
        #         'created': created,
        #         'task': delayed_task_to_dict(task)
        #     })
        # elif workflow['type'] == 'Every':
        #     eta, seconds = parse_task_eta(workflow)
        #     schedule, _ = IntervalSchedule.objects.get_or_create(every=seconds, period=IntervalSchedule.SECONDS)
        #     task, created = RepeatingTask.objects.get_or_create(
        #         user=user,
        #         interval=schedule,
        #         agent=agent,
        #         eta=eta,
        #         workflow_owner=workflow['repo']['owner']['login'],
        #         workflow_name=workflow['repo']['name'],
        #         name=f"User {user.username} workflow {workflow['repo']['name']} agent {agent.name} {schedule} repeating",
        #         task='plantit.celery_tasks.create_and_submit_task',
        #         args=json.dumps([user.username, agent.name, workflow]))
        #     return JsonResponse({
        #         'created': created,
        #         'task': repeating_task_to_dict(task)
        #     })

        else:
            raise ValueError(f"Unsupported task type (expected: Now, Later, or Periodically)")


@login_required
def get_by_owner(request, owner):
    # params = request.query_params
    # page = params.get('page') if 'page' in params else -1

    try:
        user = User.objects.get(username=owner)
    except:
        return HttpResponseNotFound()

    tasks = Task.objects.filter(user=user)
    paginator = Paginator(tasks, 20)
    page = paginator.get_page(int(request.GET.get('page', 1)))

    data = {
        'previous_page': page.has_previous() and page.previous_page_number() or None,
        'next_page': page.has_next() and page.next_page_number() or None,
        'tasks': [task_to_dict(task) for task in list(page)]
    }
    return JsonResponse(data)
    # JsonResponse({'tasks': [task_to_dict(t) for t in tasks]})

    # TODO we still eventually need paging
    # if 'running' in params and params.get('running') == 'True':
    #     tasks = [t for t in tasks.filter(completed__isnull=True).order_by('-created') if not t.is_complete]
    # elif 'running' in params and params.get('running') == 'False':
    #     tasks = [t for t in tasks if t.is_complete]
    #     if page > -1:
    #         start = int(page) * 20
    #         count = start + 20
    #         tasks = tasks[start:(start + count)]
    # else:
    #     if page > -1:
    #         start = int(page) * 20
    #         count = start + 20
    #         tasks = tasks[start:(start + count)]


@login_required
def get_by_owner_and_name(request, owner, name):
    try:
        user = User.objects.get(username=owner)
        task = Task.objects.get(user=user, name=name)
        return JsonResponse(task_to_dict(task))
    except Task.DoesNotExist:
        return HttpResponseNotFound()


@login_required
def transfer_to_cyverse(request, owner, name):
    body = json.loads(request.body.decode('utf-8'))
    auth = parse_task_auth_options(body['auth'])
    transfer_path = body['path']

    # find the task
    try:
        user = User.objects.get(username=owner)
        task = Task.objects.get(user=user, name=name)
    except:
        return HttpResponseNotFound()
    if not task.is_complete: return HttpResponseBadRequest('task incomplete')

    # compose command
    command = f"plantit terrain push {transfer_path} -p {join(task.agent.workdir, task.workdir)} "
    command = command + ' ' + ' '.join(['--include_name ' + name for name in get_included_by_name(task)])
    command = command + ' ' + ' '.join(['--include_pattern ' + pattern for pattern in get_included_by_pattern(task)])
    command += f" --terrain_token '{task.user.profile.cyverse_access_token}'"

    # run command
    ssh = get_task_ssh_client(task, auth)
    with ssh:
        for line in execute_command(ssh=ssh, precommand=task.agent.pre_commands, command=command, directory=task.agent.workdir, allow_stderr=True):
            logger.info(f"[{task.agent.name}] {line}")

    # update task
    task.transfer_path = transfer_path
    task.transferred = True
    task.save()

    return JsonResponse(task_to_dict(task))


# @login_required
# def get_3d_model(request, guid):
#     body = json.loads(request.body.decode('utf-8'))
#     path = body['path']
#     file = path.rpartition('/')[2]
#     auth = parse_task_auth_options(body['auth'])
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
def get_output_file(request, owner, name):
    try:
        user = User.objects.get(username=owner)
        task = Task.objects.get(user=user, name=name)
    except Task.DoesNotExist:
        return HttpResponseNotFound()

    body = json.loads(request.body.decode('utf-8'))
    print(body)
    path = body['path']
    auth = parse_task_auth_options(body['auth'])

    ssh = get_task_ssh_client(task, auth)
    workdir = join(task.agent.workdir, task.workdir)

    with ssh:
        with ssh.client.open_sftp() as sftp:
            file_path = join(workdir, path)
            print(f"Downloading {file_path}")

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
def get_task_logs(request, owner, name):
    try:
        user = User.objects.get(username=owner)
        task = Task.objects.get(user=user, name=name)
    except Task.DoesNotExist:
        return HttpResponseNotFound()

    log_path = get_task_orchestrator_log_file_path(task)
    return FileResponse(open(log_path, 'rb')) if Path(log_path).is_file() else HttpResponseNotFound()


@login_required
def get_task_logs_content(request, owner, name):
    try:
        user = User.objects.get(username=owner)
        task = Task.objects.get(user=user, name=name)
    except Task.DoesNotExist:
        return HttpResponseNotFound()

    log_path = get_task_orchestrator_log_file_path(task)
    if not Path(log_path).is_file():
        return HttpResponseNotFound()

    with open(log_path, 'r') as log_file:
        return JsonResponse({'lines': log_file.readlines()})


@login_required
def get_scheduler_logs(request, owner, name):
    try:
        user = User.objects.get(username=owner)
        task = Task.objects.get(user=user, name=name)
    except Task.DoesNotExist:
        return HttpResponseNotFound()

    body = json.loads(request.body.decode('utf-8'))
    auth = parse_task_auth_options(body['auth'])

    with open(get_task_scheduler_log_file_path(task)) as file:
        return JsonResponse({'lines': file.readlines()})

    # ssh = get_task_ssh_client(task, auth)
    # workdir = join(task.agent.workdir, task.workdir)
    # log_file = get_task_scheduler_log_file_name(task)

    # with ssh:
    #     with ssh.client.open_sftp() as sftp:
    #         stdin, stdout, stderr = ssh.client.exec_command(
    #             'test -e {0} && echo exists'.format(join(workdir, log_file)))
    #         errs = stderr.read()
    #         if errs:
    #             raise Exception(f"Failed to check existence of {log_file}: {errs}")
    #         if not stdout.read().decode().strip() == 'exists':
    #             return HttpResponseNotFound()

    #         with tempfile.NamedTemporaryFile() as tf:
    #             sftp.chdir(workdir)
    #             sftp.get(log_file, tf.name)
    #             return FileResponse(open(tf.name, 'rb'))


@login_required
def get_scheduler_logs_content(request, owner, name):
    try:
        user = User.objects.get(username=owner)
        task = Task.objects.get(user=user, name=name)
    except Task.DoesNotExist:
        return HttpResponseNotFound()

    body = json.loads(request.body.decode('utf-8'))
    auth = parse_task_auth_options(body['auth'])

    with open(get_task_scheduler_log_file_path(task)) as file:
        return JsonResponse({'lines': file.readlines()})

    # ssh = get_task_ssh_client(task, auth)
    # workdir = join(task.agent.workdir, task.workdir)
    # log_file = get_task_scheduler_log_file_name(task)

    # with ssh:
    #     with ssh.client.open_sftp() as sftp:
    #         stdin, stdout, stderr = ssh.client.exec_command(
    #             'test -e {0} && echo exists'.format(join(workdir, log_file)))
    #         errs = stderr.read()
    #         if errs:
    #             raise Exception(f"Failed to check existence of {log_file}: {errs}")
    #         if not stdout.read().decode().strip() == 'exists':
    #             return HttpResponseNotFound()

    #         with tempfile.NamedTemporaryFile() as tf:
    #             sftp.chdir(workdir)
    #             sftp.get(log_file, tf.name)
    #             with open(tf.name, 'r') as log_file:
    #                 return JsonResponse({'lines': log_file.readlines()})


@login_required
def get_agent_logs(request, owner, name):
    try:
        user = User.objects.get(username=owner)
        task = Task.objects.get(user=user, name=name)
    except Task.DoesNotExist:
        return HttpResponseNotFound()

    body = json.loads(request.body.decode('utf-8'))
    auth = parse_task_auth_options(body['auth'])

    with open(get_task_agent_log_file_path(task)) as file:
        return JsonResponse({'lines': file.readlines()})

    # ssh = get_task_ssh_client(task, auth)
    # workdir = join(task.agent.workdir, task.workdir)
    # log_file = get_task_agent_log_file_name(task)

    # with ssh:
    #     with ssh.client.open_sftp() as sftp:
    #         stdin, stdout, stderr = ssh.client.exec_command(
    #             'test -e {0} && echo exists'.format(join(workdir, log_file)))
    #         errs = stderr.read()
    #         if errs:
    #             raise Exception(f"Failed to check existence of {log_file}: {errs}")
    #         if not stdout.read().decode().strip() == 'exists':
    #             return HttpResponseNotFound()

    #         with tempfile.NamedTemporaryFile() as tf:
    #             sftp.chdir(workdir)
    #             sftp.get(log_file, tf.name)
    #             return FileResponse(open(tf.name, 'rb'))


@login_required
def get_agent_logs_content(request, owner, name):
    try:
        user = User.objects.get(username=owner)
        task = Task.objects.get(user=user, name=name)
    except Task.DoesNotExist:
        return HttpResponseNotFound()

    body = json.loads(request.body.decode('utf-8'))
    auth = parse_task_auth_options(body['auth'])

    with open(get_task_agent_log_file_path(task)) as file:
        return JsonResponse({'lines': file.readlines()})

    # ssh = get_task_ssh_client(task, auth)
    # workdir = join(task.agent.workdir, task.workdir)
    # log_file = get_task_agent_log_file_name(task)

    # with ssh:
    #     with ssh.client.open_sftp() as sftp:
    #         stdin, stdout, stderr = ssh.client.exec_command(
    #             'test -e {0} && echo exists'.format(join(workdir, log_file)))
    #         errs = stderr.read()
    #         if errs:
    #             raise Exception(f"Failed to check existence of {log_file}: {errs}")
    #         if not stdout.read().decode().strip() == 'exists':
    #             return HttpResponseNotFound()

    #         with tempfile.NamedTemporaryFile() as tf:
    #             sftp.chdir(workdir)
    #             sftp.get(log_file, tf.name)
    #             with open(tf.name, 'r') as log_file:
    #                 return JsonResponse({'lines': log_file.readlines()})


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
#     auth = parse_task_auth_options(body['auth'])
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
def cancel(request, owner, name):
    try:
        user = User.objects.get(username=owner)
        task = Task.objects.get(user=user, name=name)
    except:
        return HttpResponseNotFound()

    if task.is_complete:
        return HttpResponse(f"User {owner}'s task {name} already completed")

    if task.agent.executor == AgentExecutor.LOCAL and task.celery_task_id is not None:
        AsyncResult(task.celery_task_id).revoke()  # cancel the Celery task
    else:
        auth = parse_task_auth_options(json.loads(request.body.decode('utf-8'))['auth'])
        cancel_task(task, auth)

    now = timezone.now()
    task.status = TaskStatus.CANCELED
    task.updated = now
    task.completed = now
    task.save()

    msg = f"Cancelled user {owner}'s task {name}"
    log_task_orchestrator_status(task, [msg])
    push_task_event(task)
    return JsonResponse({'canceled': True})


@login_required
def delete(request, owner, name):
    try:
        user = User.objects.get(username=owner)
        task = Task.objects.get(user=user, name=name)
    except:
        return HttpResponseNotFound()

    task.delete()
    tasks = list(Task.objects.filter(user=user))

    return JsonResponse({'tasks': [task_to_dict(t) for t in tasks]})


@login_required
def exists(request, owner, name):
    try:
        Task.objects.get(user=User.objects.get(username=owner), name=name)
        return JsonResponse({'exists': True})
    except Task.DoesNotExist:
        return JsonResponse({'exists': True})


@sync_to_async
@login_required
@csrf_exempt
@async_to_sync
async def status(request, owner, name):
    try:
        user = await sync_to_async(User.objects.get)(username=owner)
        task = await sync_to_async(Task.objects.get)(user=user, name=name)
    except Task.DoesNotExist:
        return HttpResponseNotFound()

    body = json.loads(request.body.decode('utf-8'))

    for chunk in body['description'].split('<br>'):
        task.status = TaskStatus.RUNNING
        for line in chunk.split('\n'):
            if 'FATAL' in line or int(body['state']) == 0:  # catch singularity build failures etc
                task.status = TaskStatus.FAILURE
            elif int(body['state']) == 6:  # catch completion
                task.status = TaskStatus.SUCCESS

            task.updated = timezone.now()
            await sync_to_async(task.save)()
            log_task_orchestrator_status(task, line)
            await push_task_event(task)

        task.updated = timezone.now()
        await sync_to_async(task.save)()

    return HttpResponse(status=200)


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
