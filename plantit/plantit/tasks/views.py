import base64
import json
import tempfile
from os.path import join
from pathlib import Path

from asgiref.sync import sync_to_async, async_to_sync
from celery.result import AsyncResult
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse, FileResponse, HttpResponseBadRequest
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from plantit import settings
from plantit.agents.models import Agent
from plantit.celery_tasks import submit_task
from plantit.redis import RedisClient
from plantit.tasks.models import Task, DelayedTask, RepeatingTask, TaskStatus
from plantit.utils import task_to_dict, create_task, parse_task_auth_options, get_task_ssh_client, get_task_orchestration_log_file_path, log_task_status, \
    push_task_event, cancel_task, delayed_task_to_dict, repeating_task_to_dict


@login_required
def get_all_or_create(request):
    user = request.user
    workflow = json.loads(request.body.decode('utf-8'))

    if request.method == 'GET':
        tasks = Task.objects.all()
        return JsonResponse({'tasks': [task_to_dict(sub) for sub in tasks]})
    elif request.method == 'POST':
        config = workflow['config']
        agent = Agent.objects.get(name=config['agent']['name'])
        if workflow['type'] == 'Now':
            # create the task
            task_name = config.get('task_name', None)
            task_guid = config.get('task_guid', None)
            if task_guid is None: return HttpResponseBadRequest()
            task = create_task(
                username=user.username,
                agent_name=agent.name,
                workflow=workflow,
                name=task_name if task_name is not None and task_name != '' else task_guid,
                guid=task_guid)

            # submit the task
            auth = parse_task_auth_options(workflow['auth'])
            submit_task.delay(task.guid, auth)
            tasks = list(Task.objects.filter(user=user))
            return JsonResponse({'tasks': [task_to_dict(t) for t in tasks]})

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

    tasks = list(Task.objects.filter(user=user))

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

    return JsonResponse({'tasks': [task_to_dict(t) for t in tasks]})


@login_required
def get_by_owner_and_name(request, owner, name):
    try:
        user = User.objects.get(username=owner)
        task = Task.objects.get(user=user, name=name)
        return JsonResponse(task_to_dict(task))
    except Task.DoesNotExist:
        return HttpResponseNotFound()


@login_required
def get_thumbnail(request, owner, name):
    path = request.GET.get('path')
    file = path.rpartition('/')[2]

    try:
        user = User.objects.get(username=owner)
        task = Task.objects.get(user=user, name=name)
    except:
        return HttpResponseNotFound()

    redis = RedisClient.get()
    preview = redis.get(f"previews/{user.username}/{task.name}/{file}")

    if preview is None or preview == b'EMPTY':
        with open(settings.NO_PREVIEW_THUMBNAIL, 'rb') as thumbnail:
            return HttpResponse(thumbnail, content_type="image/png")
    elif file.endswith('txt') or \
            file.endswith('csv') or \
            file.endswith('yml') or \
            file.endswith('yaml') or \
            file.endswith('tsv') or \
            file.endswith('out') or \
            file.endswith('err') or \
            file.endswith('log'):
        decoded = base64.b64decode(preview)
        print(f"Retrieved text file preview from cache: {file}")
        return HttpResponse(decoded, content_type="image/jpg")
    elif file.endswith('png'):
        decoded = base64.b64decode(preview)
        print(f"Retrieved PNG file preview from cache: {file}")
        return HttpResponse(decoded, content_type="image/png")
    elif file.endswith('jpg') or file.endswith('jpeg'):
        decoded = base64.b64decode(preview)
        print(f"Retrieved JPG file preview from cache: {file}")
        return HttpResponse(decoded, content_type="image/jpg")
    elif file.endswith('czi'):
        decoded = base64.b64decode(preview)
        print(f"Retrieved CZI file preview from cache: {file}")
        return HttpResponse(decoded, content_type="image/jpg")
    else:
        with open(settings.NO_PREVIEW_THUMBNAIL, 'rb') as thumbnail:
            return HttpResponse(thumbnail, content_type="image/png")


@login_required
def get_3d_model(request, guid):
    path = request.GET.get('path')
    file = path.rpartition('/')[2]

    try:
        task = Task.objects.get(guid=guid)
    except:
        return HttpResponseNotFound()

    ssh = get_task_ssh_client(task)
    workdir = join(task.agent.workdir, task.workdir)

    with tempfile.NamedTemporaryFile() as temp_file:
        with ssh:
            with ssh.client.open_sftp() as sftp:
                sftp.chdir(workdir)
                sftp.get(file, temp_file.name)
        return HttpResponse(temp_file, content_type="applications/octet-stream")


@login_required
def get_output_file(request, owner, name, file):
    try:
        user = User.objects.get(username=owner)
        task = Task.objects.get(user=user, name=name)
    except Task.DoesNotExist:
        return HttpResponseNotFound()

    ssh = get_task_ssh_client(task)
    workdir = join(task.agent.workdir, task.workdir)

    with ssh:
        with ssh.client.open_sftp() as sftp:
            file_path = join(workdir, file)
            print(f"Downloading {file_path}")

            stdin, stdout, stderr = ssh.client.exec_command(
                'test -e {0} && echo exists'.format(file_path))
            if not stdout.read().decode().strip() == 'exists':
                return HttpResponseNotFound()

            with tempfile.NamedTemporaryFile() as tf:
                sftp.chdir(workdir)
                sftp.get(file, tf.name)
                return FileResponse(open(tf.name, 'rb'))


@login_required
def get_task_logs(request, owner, name):
    try:
        user = User.objects.get(username=owner)
        task = Task.objects.get(user=user, name=name)
    except Task.DoesNotExist:
        return HttpResponseNotFound()

    log_path = get_task_orchestration_log_file_path(task)
    return FileResponse(open(log_path, 'rb')) if Path(log_path).is_file() else HttpResponseNotFound()


@login_required
def get_container_logs(request, owner, name):
    try:
        user = User.objects.get(username=owner)
        task = Task.objects.get(user=user, name=name)
    except Task.DoesNotExist:
        return HttpResponseNotFound()

    ssh = get_task_ssh_client(task)
    workdir = join(task.agent.workdir, task.workdir)
    log_file = f"plantit.{task.job_id}.out" if task.agent.launcher else f"{user.username}.{task.name}.{task.agent.name.lower()}.log"

    with ssh:
        with ssh.client.open_sftp() as sftp:
            stdin, stdout, stderr = ssh.client.exec_command(
                'test -e {0} && echo exists'.format(join(workdir, log_file)))
            errs = stderr.read()
            if errs:
                raise Exception(f"Failed to check existence of {log_file}: {errs}")
            if not stdout.read().decode().strip() == 'exists':
                return HttpResponseNotFound()

            with tempfile.NamedTemporaryFile() as tf:
                sftp.chdir(workdir)
                sftp.get(log_file, tf.name)
                return FileResponse(open(tf.name, 'rb'))


@login_required
def get_file_text(request, owner, name):
    file = request.GET.get('path')
    try:
        user = User.objects.get(username=owner)
        task = Task.objects.get(user=user, name=name)
    except Task.DoesNotExist:
        return HttpResponseNotFound()

    ssh = get_task_ssh_client(task)
    workdir = join(task.agent.workdir, task.workdir)

    with ssh:
        with ssh.client.open_sftp() as sftp:
            path = join(workdir, file)
            stdin, stdout, stderr = ssh.client.exec_command(
                'test -e {0} && echo exists'.format(path))
            errs = stderr.read()
            if errs:
                raise Exception(f"Failed to check existence of {file}: {errs}")
            if not stdout.read().decode().strip() == 'exists':
                return HttpResponseNotFound()

            stdin, stdout, stderr = ssh.client.exec_command(f"cat {path}")
            return JsonResponse({'text': stdout.readlines()})


@login_required
def cancel(request, owner, name):
    try:
        user = User.objects.get(username=owner)
        task = Task.objects.get(user=user, name=name)
    except:
        return HttpResponseNotFound()

    if task.is_complete:
        return HttpResponse(f"User {owner}'s task {name} already completed")

    if task.is_sandbox:
        AsyncResult(task.celery_task_id).revoke()  # cancel the Celery task
    else:
        cancel_task(task)  # cancel the scheduler job

    now = timezone.now()
    task.status = TaskStatus.CANCELED
    task.updated = now
    task.completed = now
    task.save()

    msg = f"Cancelled user {owner}'s task {name}"
    log_task_status(task, msg)
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
            log_task_status(task, line)
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
