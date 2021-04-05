import json
import tempfile
from os.path import join
from pathlib import Path

from celery.result import AsyncResult
from cv2 import cv2
from czifile import czifile
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse, FileResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django_celery_beat.models import IntervalSchedule
from preview_generator.manager import PreviewManager
from rest_framework.decorators import api_view

from plantit import settings
from plantit.redis import RedisClient
from plantit.runs.cluster import cancel_run
from plantit.runs.models import Run, DelayedRunTask, RepeatingRunTask
from plantit.runs.ssh import SSH
from plantit.runs.tasks import submit_run, list_run_results
from plantit.runs.thumbnail import Thumbnail
from plantit.runs.utils import update_status, map_run, submission_log_file_path, create_run, parse_eta, map_delayed_run_task, \
    map_repeating_run_task
from plantit.clusters.models import Cluster
from plantit.utils import get_repo_config


@api_view(['GET'])
@login_required
def get_by_user(request, username):
    params = request.query_params
    page = params.get('page') if 'page' in params else -1

    try:
        user = User.objects.get(username=username)
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

    return JsonResponse([map_run(run) for run in runs], safe=False)


@api_view(['GET'])
def get_total_count(request):
    runs = Run.objects.all()
    return JsonResponse({'count': len(runs)})


@api_view(['GET'])
@login_required
def list_outputs(request, id):
    redis = RedisClient.get()
    result = redis.get(f"results/{id}")
    return JsonResponse({'outputs': json.loads(result) if result is not None else []})


@api_view(['GET'])
@login_required
def get_thumbnail(request, id):
    user = request.user
    path = request.GET.get('path')
    file = path.rpartition('/')[2]
    try:
        run = Run.objects.get(guid=id)
    except:
        return HttpResponseNotFound()

    work_dir = join(run.cluster.workdir, run.work_dir)
    client = SSH(run.cluster.hostname, run.cluster.port, run.cluster.username)

    with client:
        with client.client.open_sftp() as sftp:
            stdin, stdout, stderr = client.client.exec_command(f"test -e {join(work_dir, file)} && echo exists")
            manager = PreviewManager(join(settings.MEDIA_ROOT, run.guid), create_folder=True)

            if file.endswith('txt') or \
                    file.endswith('csv') or \
                    file.endswith('yml') or \
                    file.endswith('yaml') or \
                    file.endswith('tsv') or \
                    file.endswith('out') or \
                    file.endswith('err') or \
                    file.endswith('log'):
                with tempfile.NamedTemporaryFile() as temp_file:
                    sftp.chdir(work_dir)
                    sftp.get(file, temp_file.name)
                    preview_file = manager.get_jpeg_preview(temp_file.name, width=1024, height=1024)
                    with open(preview_file, 'rb') as preview:
                        return HttpResponse(preview, content_type="image/jpg")
            elif file.endswith('png'):
                with tempfile.NamedTemporaryFile() as temp_file:
                    sftp.chdir(work_dir)
                    sftp.get(file, temp_file.name)
                    return HttpResponse(temp_file, content_type="image/png")
            elif file.endswith('jpg') or file.endswith('jpeg'):
                with tempfile.NamedTemporaryFile() as temp_file:
                    sftp.chdir(work_dir)
                    sftp.get(file, temp_file.name)
                    return HttpResponse(temp_file, content_type="image/jpeg")
            elif file.endswith('czi'):
                with tempfile.NamedTemporaryFile() as temp_file:
                    print(f"Creating thumbnail for {file}")
                    sftp.chdir(work_dir)
                    sftp.get(file, temp_file.name)
                    image = czifile.imread(temp_file.name)
                    image.shape = (image.shape[2], image.shape[3], image.shape[4])
                    success, buffer = cv2.imencode(".jpg", image)
                    buffer.tofile(temp_file.name)
                    return HttpResponse(temp_file, content_type="image/png")
            elif file.endswith('ply'):
                with tempfile.NamedTemporaryFile() as temp_file:
                    sftp.chdir(work_dir)
                    sftp.get(file, temp_file.name)
                    return HttpResponse(temp_file, content_type="applications/octet-stream")
            else:
                with open(settings.NO_PREVIEW_THUMBNAIL, 'rb') as thumbnail:
                    return HttpResponse(thumbnail, content_type="image/png")


@api_view(['GET'])
@login_required
def get_output_file(request, id, file):
    try:
        run = Run.objects.get(guid=id)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    client = SSH(run.cluster.hostname, run.cluster.port, run.cluster.username)
    work_dir = join(run.cluster.workdir, run.work_dir)

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
def get_submission_logs_text(request, id, size):
    try:
        run = Run.objects.get(guid=id)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    log_path = submission_log_file_path(run)
    if Path(log_path).is_file():
        with open(log_path, 'r') as log:
            lines = log.readlines()[-int(size):]
    else:
        return []


@api_view(['GET'])
@login_required
def get_submission_logs(request, id):
    try:
        run = Run.objects.get(guid=id)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    log_path = submission_log_file_path(run)
    return FileResponse(open(log_path, 'rb')) if Path(log_path).is_file() else HttpResponseNotFound()


@api_view(['GET'])
@login_required
def get_container_logs(request, id):
    try:
        run = Run.objects.get(guid=id)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    client = SSH(run.cluster.hostname, run.cluster.port, run.cluster.username)
    work_dir = join(run.cluster.workdir, run.work_dir)

    if run.cluster.launcher:
        log_file = f"plantit.{run.job_id}.out"
    else:
        log_file = f"{run.guid}.{run.cluster.name.lower()}.log"

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
def get_runs_by_user_and_workflow(request, username, workflow, page):
    try:
        user = User.objects.get(username=username)
        start = int(page) * 20
        count = start + 20
        runs = Run.objects.filter(user=user, workflow_name=workflow).order_by('-created')[start:(start + count)]
        return JsonResponse([map_run(run) for run in runs], safe=False)
    except:
        return HttpResponseNotFound()


@api_view(['GET'])
@login_required
def get_delayed_runs_by_user_and_workflow(request, username, workflow):
    user = User.objects.get(username=username)
    try:
        tasks = DelayedRunTask.objects.filter(user=user)
    except:
        return HttpResponseNotFound()

    tasks = [task for task in tasks if task.workflow_name == workflow]
    return JsonResponse([map_delayed_run_task(task) for task in tasks], safe=False)


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
def get_repeating_runs_by_user_and_workflow(request, username, workflow):
    user = User.objects.get(username=username)
    try:
        tasks = RepeatingRunTask.objects.filter(user=user)
    except:
        return HttpResponseNotFound()

    tasks = [task for task in tasks if task.workflow_name == workflow]
    return JsonResponse([map_repeating_run_task(task) for task in tasks], safe=False)


@api_view(['GET'])
@login_required
def toggle_repeating(request, username, workflow):
    task_name = request.GET.get('name', None)
    if task_name is None:
        return HttpResponseNotFound()

    task = RepeatingRunTask.objects.get(name=task_name)
    task.enabled = not task.enabled
    task.save()
    return JsonResponse(map_repeating_run_task(task))


@api_view(['GET'])
@login_required
def remove_repeating(request, username, workflow):
    task_name = request.GET.get('name', None)
    if task_name is None:
        return HttpResponseNotFound()

    try:
        task = RepeatingRunTask.objects.get(name=task_name)
    except:
        return HttpResponseNotFound()

    task.delete()
    return JsonResponse({'deleted': True})


@api_view(['GET', 'POST'])
@login_required
def runs(request):
    user = request.user
    workflow = request.data
    if request.method == 'GET':
        runs = Run.objects.all()
        return JsonResponse([map_run(run) for run in runs], safe=False)
    elif request.method == 'POST':
        cluster = Cluster.objects.get(name=workflow['config']['cluster']['name'])
        if request.data['type'] == 'Now':
            run = create_run(user.username, cluster.name, workflow)
            submit_run.delay(run.guid, workflow)
            return JsonResponse({'id': run.guid})
        elif request.data['type'] == 'After':
            eta, seconds = parse_eta(workflow)
            schedule, _ = IntervalSchedule.objects.get_or_create(every=seconds, period=IntervalSchedule.SECONDS)
            task, created = DelayedRunTask.objects.get_or_create(
                user=user,
                interval=schedule,
                cluster=cluster,
                eta=eta,
                one_off=True,
                workflow_owner=workflow['repo']['owner']['login'],
                workflow_name=workflow['repo']['name'],
                name=f"User {user.username} workflow {workflow['repo']['name']} cluster {cluster.name} {schedule} once",
                task='plantit.runs.tasks.create_and_submit_run',
                args=json.dumps([user.username, cluster.name, workflow]))
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
                cluster=cluster,
                eta=eta,
                workflow_owner=workflow['repo']['owner']['login'],
                workflow_name=workflow['repo']['name'],
                name=f"User {user.username} workflow {workflow['repo']['name']} cluster {cluster.name} {schedule} repeating",
                task='plantit.runs.tasks.create_and_submit_run',
                args=json.dumps([user.username, cluster.name, workflow]))
            return JsonResponse({
                'created': created,
                'task': map_repeating_run_task(task)
            })
        else:
            raise ValueError(f"Unsupported submission type (expected: Now, Later, or Periodically)")


@api_view(['GET'])
@login_required
def run(request, id):
    try:
        run = Run.objects.get(guid=id)
        return JsonResponse(map_run(run, True))
    except Run.DoesNotExist:
        return JsonResponse({
            'id': id,
            'job_id': None,
            'job_status': None,
            'job_walltime': None,
            'work_dir': None,
            'cluster': None,
            'created': None,
            'updated': None,
            'completed': None,
            'workflow_owner': None,
            'workflow_name': None,
            'tags': [],
            'is_complete': False,
            'is_success': False,
            'is_failure': False,
            'is_cancelled': False,
            'is_timeout': False,
        })


@api_view(['GET'])
@login_required
def cancel(request, id):
    try:
        run = Run.objects.get(guid=id)
    except:
        return HttpResponseNotFound()

    if run.is_complete:
        return HttpResponse(f"Run {id} is no longer running")

    message = f"Cancelled run {id}"
    if run.is_sandbox:
        # cancel the Celery task
        AsyncResult(run.submission_id).revoke()
        now = timezone.now()
        run.job_status = 'CANCELLED'
        run.updated = now
        run.completed = now
        run.save()

        update_status(run, message)
        return HttpResponse(message)
    else:
        # cancel the cluster scheduler job
        cancel_run(run)
        now = timezone.now()
        run.job_status = 'CANCELLED'
        run.updated = now
        run.completed = now
        run.save()

        update_status(run, message)
        return HttpResponse(message)


@api_view(['GET'])
@login_required
def delete(request, id):
    try:
        run = Run.objects.get(guid=id)
    except:
        return HttpResponseNotFound()

    if not run.is_complete:
        print(f"Run is not complete")
        return HttpResponse({'deleted': False})

    run.delete()
    return HttpResponse({'deleted': True})


@api_view(['POST'])
@login_required
@csrf_exempt
def status(request, id):
    status = request.data

    try:
        run = Run.objects.get(guid=id)
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

            update_status(run, line)

        run.updated = timezone.now()
        run.save()


    return HttpResponse(status=200)
