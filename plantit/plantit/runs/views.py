import base64
import json
import tempfile
from os.path import join
from pathlib import Path

from celery.result import AsyncResult
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse, FileResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django_celery_beat.models import IntervalSchedule
from rest_framework.decorators import api_view

from plantit import settings
from plantit.agents.models import Agent
from plantit.redis import RedisClient
from plantit.runs.models import Run, DelayedRunTask, RepeatingRunTask
from plantit.runs.tasks import submit_run
from plantit.runs.utils import update_run_status, map_run, get_run_submission_log_file_path, create_run, parse_eta, map_delayed_run_task, \
    map_repeating_run_task, cancel_run
from plantit.ssh import SSH


@api_view(['GET', 'POST'])
@login_required
def get_all_or_create(request):
    user = request.user
    workflow = request.data
    if request.method == 'GET':
        runs = Run.objects.all()
        return JsonResponse([map_run(run) for run in runs], safe=False)
    elif request.method == 'POST':
        agent = Agent.objects.get(name=workflow['config']['agent']['name'])
        if request.data['type'] == 'Now':
            run = create_run(user.username, agent.name, workflow, workflow['config'].get('run_name', None))
            submit_run.delay(run.guid, workflow)
            return JsonResponse({'name': run.name})
        elif request.data['type'] == 'After':
            eta, seconds = parse_eta(workflow)
            schedule, _ = IntervalSchedule.objects.get_or_create(every=seconds, period=IntervalSchedule.SECONDS)
            task, created = DelayedRunTask.objects.get_or_create(
                user=user,
                interval=schedule,
                agent=agent,
                eta=eta,
                one_off=True,
                workflow_owner=workflow['repo']['owner']['login'],
                workflow_name=workflow['repo']['name'],
                name=f"User {user.username} workflow {workflow['repo']['name']} agent {agent.name} {schedule} once",
                task='plantit.runs.tasks.create_and_submit_run',
                args=json.dumps([user.username, agent.name, workflow]))
            return JsonResponse({
                'created': created,
                'task': map_delayed_run_task(task)
            })
        elif request.data['type'] == 'Every':
            eta, seconds = parse_eta(workflow)
            schedule, _ = IntervalSchedule.objects.get_or_create(every=seconds, period=IntervalSchedule.SECONDS)
            task, created = RepeatingRunTask.objects.get_or_create(
                user=user,
                interval=schedule,
                agent=agent,
                eta=eta,
                workflow_owner=workflow['repo']['owner']['login'],
                workflow_name=workflow['repo']['name'],
                name=f"User {user.username} workflow {workflow['repo']['name']} agent {agent.name} {schedule} repeating",
                task='plantit.runs.tasks.create_and_submit_run',
                args=json.dumps([user.username, agent.name, workflow]))
            return JsonResponse({
                'created': created,
                'task': map_repeating_run_task(task)
            })
        else:
            raise ValueError(f"Unsupported submission type (expected: Now, Later, or Periodically)")


@api_view(['GET'])
@login_required
def get_by_owner(request, owner):
    params = request.query_params
    page = params.get('page') if 'page' in params else -1

    try:
        user = User.objects.get(username=owner)
    except:
        return HttpResponseNotFound()

    runs = Run.objects.filter(user=user)

    if 'running' in params and params.get('running') == 'True':
        runs = [run for run in runs.filter(completed__isnull=True).order_by('-created') if not run.is_complete]
    elif 'running' in params and params.get('running') == 'False':
        runs = [run for run in runs if run.is_complete]
        if page > -1:
            start = int(page) * 20
            count = start + 20
            runs = runs[start:(start + count)]
    else:
        if page > -1:
            start = int(page) * 20
            count = start + 20
            runs = runs[start:(start + count)]

    runs = [map_run(run) for run in runs]
    return JsonResponse(runs, safe=False)


@api_view(['GET'])
@login_required
def get_by_owner_and_name(request, owner, name):
    try:
        user = User.objects.get(username=owner)
        run = Run.objects.get(user=user, name=name)
        return JsonResponse(map_run(run))
    except Run.DoesNotExist:
        return HttpResponseNotFound()


@api_view(['GET'])
@login_required
def get_thumbnail(request, owner, name):
    path = request.GET.get('path')
    file = path.rpartition('/')[2]

    try:
        user = User.objects.get(username=owner)
        run = Run.objects.get(user=user, name=name)
    except:
        return HttpResponseNotFound()

    redis = RedisClient.get()
    preview = redis.get(f"previews/{user.username}/{run.name}/{file}")

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


@api_view(['GET'])
@login_required
def get_output_file(request, owner, name, file):
    try:
        user = User.objects.get(username=owner)
        run = Run.objects.get(user=user, name=name)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    client = SSH(run.agent.hostname, run.agent.port, run.agent.username)
    work_dir = join(run.agent.workdir, run.workdir)

    with client:
        with client.client.open_sftp() as sftp:
            file_path = join(work_dir, file)
            print(f"Downloading {file_path}")

            stdin, stdout, stderr = client.client.exec_command(
                'test -e {0} && echo exists'.format(file_path))
            if not stdout.read().decode().strip() == 'exists':
                return HttpResponseNotFound()

            with tempfile.NamedTemporaryFile() as tf:
                sftp.chdir(work_dir)
                sftp.get(file, tf.name)
                return FileResponse(open(tf.name, 'rb'))


@api_view(['GET'])
@login_required
def get_submission_logs(request, owner, name):
    try:
        user = User.objects.get(username=owner)
        run = Run.objects.get(user=user, name=name)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    log_path = get_run_submission_log_file_path(run)
    return FileResponse(open(log_path, 'rb')) if Path(log_path).is_file() else HttpResponseNotFound()


@api_view(['GET'])
@login_required
def get_container_logs(request, owner, name):
    try:
        user = User.objects.get(username=owner)
        run = Run.objects.get(user=user, name=name)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    client = SSH(run.agent.hostname, run.agent.port, run.agent.username)
    work_dir = join(run.agent.workdir, run.workdir)

    if run.agent.launcher:
        log_file = f"plantit.{run.job_id}.out"
    else:
        log_file = f"{user.username}.{run.name}.{run.agent.name.lower()}.log"

    with client:
        with client.client.open_sftp() as sftp:
            stdin, stdout, stderr = client.client.exec_command(
                'test -e {0} && echo exists'.format(join(work_dir, log_file)))
            errs = stderr.read()
            if errs:
                raise Exception(f"Failed to check existence of {log_file}: {errs}")
            if not stdout.read().decode().strip() == 'exists':
                return HttpResponseNotFound()

            with tempfile.NamedTemporaryFile() as tf:
                sftp.chdir(work_dir)
                sftp.get(log_file, tf.name)
                return FileResponse(open(tf.name, 'rb'))


@api_view(['GET'])
@login_required
def get_file_text(request, owner, name):
    file = request.GET.get('path')
    try:
        user = User.objects.get(username=owner)
        run = Run.objects.get(user=user, name=name)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    client = SSH(run.agent.hostname, run.agent.port, run.agent.username)
    work_dir = join(run.agent.workdir, run.workdir)

    with client:
        with client.client.open_sftp() as sftp:
            path = join(work_dir, file)
            stdin, stdout, stderr = client.client.exec_command(
                'test -e {0} && echo exists'.format(path))
            errs = stderr.read()
            if errs:
                raise Exception(f"Failed to check existence of {file}: {errs}")
            if not stdout.read().decode().strip() == 'exists':
                return HttpResponseNotFound()

            stdin, stdout, stderr = client.client.exec_command(f"cat {path}")
            return JsonResponse({'text': stdout.readlines()})


@api_view(['GET'])
@login_required
def remove_delayed(request):
    task_name = request.GET.get('name', None)
    if task_name is None:
        return HttpResponseNotFound()

    try:
        task = DelayedRunTask.objects.get(name=task_name)
    except:
        return HttpResponseNotFound()

    task.delete()
    return JsonResponse({'deleted': True})


@api_view(['GET'])
@login_required
def toggle_repeating(request, owner, workflow_name):
    task_name = request.GET.get('name', None)
    if task_name is None:
        return HttpResponseNotFound()

    task = RepeatingRunTask.objects.get(name=task_name)
    task.enabled = not task.enabled
    task.save()
    return JsonResponse(map_repeating_run_task(task))


@api_view(['GET'])
@login_required
def remove_repeating(request, owner, workflow_name):
    task_name = request.GET.get('name', None)
    if task_name is None:
        return HttpResponseNotFound()

    try:
        task = RepeatingRunTask.objects.get(name=task_name)
    except:
        return HttpResponseNotFound()

    task.delete()
    return JsonResponse({'deleted': True})


# @api_view(['GET'])
# @login_required
# def get_by_guid(request, guid):
#     try:
#         run = Run.objects.get(guid=guid)
#         return JsonResponse(map_run(run))
#     except Run.DoesNotExist:
#         return HttpResponseNotFound()


@api_view(['GET'])
@login_required
def cancel(request, owner, name):
    try:
        user = User.objects.get(username=owner)
        run = Run.objects.get(user=user, name=name)
    except:
        return HttpResponseNotFound()

    if run.is_complete:
        return HttpResponse(f"User {owner}'s run {name} already completed")

    message = f"Cancelled user {owner}'s run {name}"
    if run.is_sandbox:
        # cancel the Celery task
        AsyncResult(run.submission_id).revoke()
        now = timezone.now()
        run.job_status = 'CANCELLED'
        run.updated = now
        run.completed = now
        run.save()

        update_run_status(run, message)
        return HttpResponse(message)
    else:
        # cancel the scheduler job
        cancel_run(run)
        now = timezone.now()
        run.job_status = 'CANCELLED'
        run.updated = now
        run.completed = now
        run.save()

        update_run_status(run, message)
        return HttpResponse(message)


@api_view(['GET'])
@login_required
def delete(request, owner, name):
    try:
        user = User.objects.get(username=owner)
        run = Run.objects.get(user=user, name=name)
    except:
        return HttpResponseNotFound()

    try:
        run.delete()
        return JsonResponse({'deleted': True})
    except:
        return JsonResponse({'deleted': False})


@api_view(['GET'])
@login_required
def exists(request, owner, name):
    try:
        Run.objects.get(user=User.objects.get(username=owner), name=name)
        return JsonResponse({'exists': True})
    except Run.DoesNotExist:
        return JsonResponse({'exists': True})


@api_view(['POST'])
@login_required
@csrf_exempt
def status(request, owner, name):
    status = request.data

    try:
        user = User.objects.get(username=owner)
        run = Run.objects.get(user=user, name=name)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    for chunk in status['description'].split('<br>'):
        run.job_status = 'RUNNING'
        for line in chunk.split('\n'):
            # catch singularity build failures etc
            if 'FATAL' in line or int(status['state']) == 0:
                run.job_status = 'FAILURE'
                run.updated = timezone.now()
                run.save()
            elif int(status['state']) == 6:
                run.job_status = 'SUCCESS'
                run.updated = timezone.now()
                run.save()

            update_run_status(run, line)

        run.updated = timezone.now()
        run.save()

    return HttpResponse(status=200)


@api_view(['GET'])
@login_required
def search(request, owner, workflow_name, page):
    try:
        user = User.objects.get(username=owner)
        start = int(page) * 20
        count = start + 20
        runs = Run.objects.filter(user=user, workflow_name=workflow_name).order_by('-created')[start:(start + count)]
        return JsonResponse([map_run(run) for run in runs], safe=False)
    except:
        return HttpResponseNotFound()


@api_view(['GET'])
@login_required
def search_delayed(request, owner, workflow_name):
    user = User.objects.get(username=owner)
    try:
        tasks = DelayedRunTask.objects.filter(user=user)
    except:
        return HttpResponseNotFound()

    tasks = [task for task in tasks if task.workflow_name == workflow_name]
    return JsonResponse([map_delayed_run_task(task) for task in tasks], safe=False)


@api_view(['GET'])
@login_required
def search_repeating(request, owner, workflow_name):
    user = User.objects.get(username=owner)
    try:
        tasks = RepeatingRunTask.objects.filter(user=user)
    except:
        return HttpResponseNotFound()

    tasks = [task for task in tasks if task.workflow_name == workflow_name]
    return JsonResponse([map_repeating_run_task(task) for task in tasks], safe=False)
