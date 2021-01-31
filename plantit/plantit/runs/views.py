import os
import os
import tempfile
from os.path import join
from pathlib import Path

from celery.result import AsyncResult
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse, FileResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from plantit import settings
from plantit.celery import app
from plantit.runs.models import Run
from plantit.runs.ssh import SSH
from plantit.runs.tasks import submit_run
from plantit.runs.thumbnail import Thumbnail
from plantit.runs.utils import update_local_log, stat_log, update_target_log
from plantit.utils import get_repo_config


@api_view(['GET'])
@login_required
def get_runs_by_user(request, username, page):
    start = int(page) * 20
    count = start + 20

    try:
        user = User.objects.get(username=username)
        runs = Run.objects.filter(user=user).order_by('-created')[start:(start + count)]
        return JsonResponse([__convert_run(run) for run in runs], safe=False)
    except:
        return HttpResponseNotFound()


@api_view(['GET'])
def get_total_count(request):
    runs = Run.objects.all()
    return JsonResponse({'count': len(runs)})


@api_view(['GET'])
@login_required
def list_outputs(request, id):
    try:
        run = Run.objects.get(submission_task_id=id)
        flow_config = get_repo_config(run.flow_name, run.flow_owner, run.user.profile.github_token)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    included_by_name = ((flow_config['output']['include']['names'] if 'names' in flow_config['output']['include'] else [])) if 'output' in flow_config else []  # [f"{run.task_id}.zip"]
    included_by_name.append(f"{run.submission_task_id}.{run.target.name.lower()}.log")
    if run.job_id is not None and run.job_id != '':
        included_by_name.append(f"plantit.{run.job_id}.out")
        included_by_name.append(f"plantit.{run.job_id}.err")
    included_by_pattern = (flow_config['output']['include']['patterns'] if 'patterns' in flow_config['output']['include'] else []) if 'output' in flow_config else []

    client = SSH(run.target.hostname, run.target.port, run.target.username)
    work_dir = join(run.target.workdir, run.work_dir)
    outputs = []
    seen = []

    with client:
        with client.client.open_sftp() as sftp:
            for file in included_by_name:
                file_path = join(work_dir, file)
                stdin, stdout, stderr = client.client.exec_command(f"test -e {file_path} && echo exists")
                errs = stderr.read()
                if errs:
                    raise Exception(f"Failed to check existence of {file}: {errs}")
                output = {
                    'name': file,
                    'exists': stdout.read().decode().strip() == 'exists'
                }
                seen.append(output['name'])
                outputs.append(output)

            try:
                for f in sftp.listdir(work_dir):
                    if any(pattern in f for pattern in included_by_pattern):
                        if not any(s == f for s in seen):
                            outputs.append({
                                'name': f,
                                'exists': True
                            })
            except:
                return JsonResponse({'outputs': []})

    return JsonResponse({'outputs': outputs})


@api_view(['GET'])
@login_required
def get_thumbnail(request, id, file):
    try:
        run = Run.objects.get(submission_task_id=id)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    client = SSH(run.target.hostname, run.target.port, run.target.username)
    work_dir = join(run.target.workdir, run.work_dir)

    with client:
        with client.client.open_sftp() as sftp:
            stdin, stdout, stderr = client.client.exec_command(f"test -e {join(work_dir, file)} && echo exists")
            errs = stderr.read()
            if errs:
                raise Exception(f"Failed to check existence of {file}: {errs}")

            run_dir = join(settings.MEDIA_ROOT, run.submission_task_id)
            thumbnail_path = join(run_dir, file)
            thumbnail_name_lower = file.lower()

            # make thumbnail directory for this run if it does not already exist
            Path(run_dir).mkdir(exist_ok=True, parents=True)

            if file.endswith('txt') or file.endswith('csv') or file.endswith('yml') or file.endswith('yaml') or file.endswith('tsv') or file.endswith('out') or file.endswith('err') or file.endswith('log'):
                with tempfile.NamedTemporaryFile() as temp_file, open(thumbnail_path, 'wb') as thumbnail_file:
                    # stdin, stdout, stderr = client.client.exec_command('test -e {0} && echo exists'.format(join(work_dir, log_file)))
                    # errs = stderr.read()
                    # if errs:
                    #     raise Exception(f"Failed to check existence of {log_file}: {errs}")
                    # if not stdout.read().decode().strip() == 'exists':
                    #     return HttpResponseNotFound()

                    sftp.chdir(work_dir)
                    sftp.get(file, temp_file.name)

                    with tempfile.NamedTemporaryFile() as tf:
                        sftp.chdir(work_dir)
                        sftp.get(file, tf.name)
                        with open(tf.name, 'r') as file:
                            lines = file.readlines()
                            return HttpResponse(lines, content_type='text/plain')

            with tempfile.NamedTemporaryFile() as temp_file, open(thumbnail_path, 'wb') as thumbnail_file:
                print(f"Creating new thumbnail: {thumbnail_path}")
                sftp.chdir(work_dir)
                sftp.get(file, temp_file.name)
                return HttpResponse(temp_file, content_type="image/png")
                # thumbnail = Thumbnail(source=temp_file).generate()
                # thumbnail_file.write(thumbnail.read())

            if Path(thumbnail_path).exists():
                print(f"Using existing thumbnail: {thumbnail_path}")
                return redirect(thumbnail_path)
                # thumbnail = open(thumbnail_path, 'rb')
            else:
                with tempfile.NamedTemporaryFile() as temp_file, open(thumbnail_path, 'wb') as thumbnail_file:
                    print(f"Creating new thumbnail: {thumbnail_path}")
                    sftp.chdir(work_dir)
                    sftp.get(file, temp_file.name)
                    thumbnail = Thumbnail(source=temp_file).generate()
                    thumbnail_file.write(thumbnail.read())

            if thumbnail_name_lower.endswith('png'):
                return HttpResponse(thumbnail, content_type="image/png")
            elif thumbnail_name_lower.endswith('jpg') or thumbnail_name_lower.endswith('jpeg'):
                return HttpResponse(thumbnail, content_type="image/jpg")
            else:
                return HttpResponseNotFound()


@api_view(['GET'])
@login_required
def get_output_file(request, id, file):
    try:
        run = Run.objects.get(submission_task_id=id)
        # flow_config = get_repo_config(run.flow_name, run.flow_owner, run.user.profile.github_token)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    client = SSH(run.target.hostname, run.target.port, run.target.username)
    work_dir = join(run.target.workdir, run.work_dir)

    with client:
        with client.client.open_sftp() as sftp:
            file_path = join(work_dir, file)
            stdin, stdout, stderr = client.client.exec_command(
                'test -e {0} && echo exists'.format(file_path))
            errs = stderr.read()
            if errs:
                raise Exception(f"Failed to check existence of {file}: {errs}")
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
        run = Run.objects.get(submission_task_id=id)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    log_path = join(os.environ.get('RUNS_LOGS'), f"{run.submission_task_id}.plantit.log")
    if Path(log_path).is_file():
        with open(log_path, 'r') as log:
            lines = log.readlines()[-int(size):]
            return HttpResponse(lines, content_type='text/plain')
    else:
        return HttpResponseNotFound()


@api_view(['GET'])
@login_required
def get_submission_logs(request, id):
    try:
        run = Run.objects.get(submission_task_id=id)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    log_path = join(os.environ.get('RUNS_LOGS'), f"{run.submission_task_id}.plantit.log")
    return FileResponse(open(log_path, 'rb')) if Path(log_path).is_file() else HttpResponseNotFound()



@api_view(['GET'])
@login_required
def get_target_logs_text(request, id, size):
    try:
        run = Run.objects.get(submission_task_id=id)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    client = SSH(run.target.hostname, run.target.port, run.target.username)
    work_dir = join(run.target.workdir, run.work_dir)
    log_file = f"{run.submission_task_id}.{run.target.name.lower()}.log"

    with client:
        with client.client.open_sftp() as sftp:
            stdin, stdout, stderr = client.client.exec_command('test -e {0} && echo exists'.format(join(work_dir, log_file)))
            errs = stderr.read()
            if errs:
                raise Exception(f"Failed to check existence of {log_file}: {errs}")
            if not stdout.read().decode().strip() == 'exists':
                return HttpResponseNotFound()

            with tempfile.NamedTemporaryFile() as tf:
                sftp.chdir(work_dir)
                sftp.get(log_file, tf.name)
                with open(tf.name, 'r') as file:
                    lines = file.readlines()[-int(size):]
                    return HttpResponse(lines, content_type='text/plain')


@api_view(['GET'])
@login_required
def get_target_logs(request, id):
    try:
        run = Run.objects.get(submission_task_id=id)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    client = SSH(run.target.hostname, run.target.port, run.target.username)
    work_dir = join(run.target.workdir, run.work_dir)
    log_file = f"{run.submission_task_id}.{run.target.name.lower()}.log"

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
def get_container_logs_text(request, id, size):
    try:
        run = Run.objects.get(submission_task_id=id)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    client = SSH(run.target.hostname, run.target.port, run.target.username)
    work_dir = join(run.target.workdir, run.work_dir)
    log_file = f"{run.submission_task_id}.{run.target.name.lower()}.log"

    with client:
        with client.client.open_sftp() as sftp:
            stdin, stdout, stderr = client.client.exec_command('test -e {0} && echo exists'.format(join(work_dir, log_file)))
            errs = stderr.read()
            if errs:
                raise Exception(f"Failed to check existence of {log_file}: {errs}")
            if not stdout.read().decode().strip() == 'exists':
                return HttpResponseNotFound()

            with tempfile.NamedTemporaryFile() as tf:
                sftp.chdir(work_dir)
                sftp.get(log_file, tf.name)
                with open(tf.name, 'r') as file:
                    lines = file.readlines()[-int(size):]
                    return HttpResponse(lines, content_type='text/plain')


@api_view(['GET'])
@login_required
def get_container_logs(request, id):
    try:
        run = Run.objects.get(submission_task_id=id)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    client = SSH(run.target.hostname, run.target.port, run.target.username)
    work_dir = join(run.target.workdir, run.work_dir)
    log_file = f"{run.submission_task_id}.{run.target.name.lower()}.log"

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


def __convert_run(run: Run):
    task = AsyncResult(run.submission_task_id, app=app)
    log_updated = stat_log(task.id)
    return {
        'id': run.submission_task_id,
        'job_id': run.job_id,
        'job_status': run.job_status,
        'job_walltime': run.job_walltime,
        'completion_status': run.completion_status,
        'work_dir': run.work_dir,
        'target': run.target.name,
        'created': run.created,
        'timeout': run.timeout,
        'updated': task.date_done.replace(tzinfo=timezone.utc) if task.ready() else log_updated if log_updated is not None else run.created,
        'flow_owner': run.flow_owner,
        'flow_name': run.flow_name,
        'tags': [str(tag) for tag in run.tags.all()],
        'is_complete': run.is_complete,
        'is_success': run.is_success,
        'is_failure': run.is_failure,
    }


@api_view(['GET', 'POST'])
@login_required
def runs(request):
    if request.method == 'GET':
        runs = Run.objects.all()
        return JsonResponse([__convert_run(run) for run in runs], safe=False)
    elif request.method == 'POST':
        task = submit_run.delay(request.user.username, request.data)
        return JsonResponse({'id': task.id})


@api_view(['GET'])
@login_required
def run(request, id):
    task = AsyncResult(id, app=app)
    try:
        run = Run.objects.get(submission_task_id=id)
        return JsonResponse(__convert_run(run))
    except Run.DoesNotExist:
        # return HttpResponseNotFound()
        return JsonResponse({
            'id': task.id,
            'work_dir': None,
            'target': None,
            'created': None,
            'timeout': None,
            'updated': None,
            'state': task.state,
            'flow_owner': None,
            'flow_name': None,
            'tags': []
        })

    # return JsonResponse({
    #     'id': run.submission_task_id,
    #     'work_dir': run.work_dir,
    #     'target': run.target.name,
    #     'created': run.created,
    #     'timeout': run.timeout,
    #     'updated': task.date_done.replace(tzinfo=timezone.utc) if task.ready() else stat_log(task.id),
    #     'state': task.status,
    #     'flow_owner': run.flow_owner,
    #     'flow_name': run.flow_name,
    #     'tags': [str(tag) for tag in run.tags.all()]
    # })


@api_view(['POST'])
@login_required
@csrf_exempt
def update_status(request, id):
    status = request.data

    try:
        run = Run.objects.get(submission_task_id=id)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    for chunk in status['description'].split('<br>'):
        for line in chunk.split('\n'):
            # skip verbose Singularity log output
            # if 'old time stamp' in line or 'image path' in line or 'Cache folder' in line or line == '':
            #     continue
            update_target_log(run.submission_task_id, run.target.name, line)
            # run.status_set.create(description=line, state=state, location=run.target.name)

    return HttpResponse(status=200)
