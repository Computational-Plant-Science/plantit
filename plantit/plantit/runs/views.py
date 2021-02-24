import json
import tempfile
from os.path import join
from pathlib import Path

from asgiref.sync import async_to_sync
from celery.result import AsyncResult
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse, FileResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from rest_framework.decorators import api_view

from plantit import settings
from plantit.runs.cluster import cancel_job
from plantit.runs.models import Run, DelayedRunTask, RepeatingRunTask
from plantit.runs.ssh import SSH
from plantit.runs.tasks import submit_run
from plantit.runs.thumbnail import Thumbnail
from plantit.runs.utils import update_status, map_run, submission_log_file_name, map_run_task, create_run, parse_eta, map_delayed_run_task, \
    map_repeating_run_task
from plantit.targets.models import Target
from plantit.targets.utils import map_target
from plantit.utils import get_repo_config


@api_view(['GET'])
@login_required
def get_runs_by_user(request, username, page):
    start = int(page) * 20
    count = start + 20

    try:
        user = User.objects.get(username=username)
        runs = Run.objects.filter(user=user).order_by('-created')[start:(start + count)]
        return JsonResponse([map_run(run) for run in runs], safe=False)
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
        run = Run.objects.get(guid=id)
        flow_config = get_repo_config(run.flow_name, run.flow_owner, run.user.profile.github_token)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    included_by_name = ((flow_config['output']['include']['names'] if 'names' in flow_config['output'][
        'include'] else [])) if 'output' in flow_config else []  # [f"{run.task_id}.zip"]
    included_by_name.append(f"{run.guid}.{run.target.name.lower()}.log")
    if run.job_id is not None and run.job_id != '':
        included_by_name.append(f"plantit.{run.job_id}.out")
        included_by_name.append(f"plantit.{run.job_id}.err")
    included_by_pattern = (
        flow_config['output']['include']['patterns'] if 'patterns' in flow_config['output']['include'] else []) if 'output' in flow_config else []

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
        run = Run.objects.get(guid=id)
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

            run_dir = join(settings.MEDIA_ROOT, run.guid)
            thumbnail_path = join(run_dir, file)
            thumbnail_name_lower = file.lower()

            # make thumbnail directory for this run if it does not already exist
            Path(run_dir).mkdir(exist_ok=True, parents=True)

            if file.endswith('txt') or file.endswith('csv') or file.endswith('yml') or file.endswith('yaml') or file.endswith('tsv') or file.endswith(
                    'out') or file.endswith('err') or file.endswith('log'):
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
        run = Run.objects.get(guid=id)
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
        run = Run.objects.get(guid=id)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    log_path = submission_log_file_name(run)
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

    log_path = submission_log_file_name(run)
    return FileResponse(open(log_path, 'rb')) if Path(log_path).is_file() else HttpResponseNotFound()


@api_view(['GET'])
@login_required
def get_container_logs(request, id):
    try:
        run = Run.objects.get(guid=id)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    client = SSH(run.target.hostname, run.target.port, run.target.username)
    work_dir = join(run.target.workdir, run.work_dir)
    log_file = f"{run.guid}.{run.target.name.lower()}.log"

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
def get_runs_by_user_and_flow(request, username, flow, page):
    try:
        user = User.objects.get(username=username)
        start = int(page) * 20
        count = start + 20
        runs = Run.objects.filter(user=user, flow_name=flow).order_by('-created')[start:(start + count)]
        return JsonResponse([map_run(run) for run in runs], safe=False)
    except:
        return HttpResponseNotFound()


@api_view(['GET'])
def get_delayed_runs_by_user_and_flow(request, username, flow):
    user = User.objects.get(username=username)
    tasks = []
    try:
        tasks = DelayedRunTask.objects.filter(user=user)
    except:
        return HttpResponseNotFound()

    tasks = [task for task in tasks if task.flow_name == flow]
    return JsonResponse([map_delayed_run_task(task) for task in tasks], safe=False)


@api_view(['GET'])
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
def get_repeating_runs_by_user_and_flow(request, username, flow):
    user = User.objects.get(username=username)
    tasks = []
    try:
        tasks = RepeatingRunTask.objects.filter(user=user)
    except:
        return HttpResponseNotFound()

    tasks = [task for task in tasks if task.flow_name == flow]
    return JsonResponse([map_repeating_run_task(task) for task in tasks], safe=False)


@api_view(['GET'])
def toggle_repeating(request, username, flow):
    task_name = request.GET.get('name', None)
    if task_name is None:
        return HttpResponseNotFound()

    task = RepeatingRunTask.objects.get(name=task_name)
    task.enabled = not task.enabled
    task.save()
    return JsonResponse(map_repeating_run_task(task))


@api_view(['GET'])
def remove_repeating(request, username, flow):
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
    flow = request.data
    if request.method == 'GET':
        runs = Run.objects.all()
        return JsonResponse([map_run(run) for run in runs], safe=False)
    elif request.method == 'POST':
        target = Target.objects.get(name=flow['config']['target']['name'])
        if request.data['type'] == 'Now':
            run = create_run(user.username, target.name, flow)
            submit_run.delay(run.guid, flow)
            return JsonResponse({'id': run.guid})
        elif request.data['type'] == 'After':
            eta, seconds = parse_eta(flow)
            schedule, _ = IntervalSchedule.objects.get_or_create(every=seconds, period=IntervalSchedule.SECONDS)
            task, created = DelayedRunTask.objects.get_or_create(
                user=user,
                interval=schedule,
                target=target,
                eta=eta,
                one_off=True,
                flow_owner=flow['repo']['owner']['login'],
                flow_name=flow['repo']['name'],
                name=f"User {user.username} flow {flow['repo']['name']} target {target.name} {schedule} once",
                task='plantit.runs.tasks.create_and_submit_run',
                args=json.dumps([user.username, target.name, flow]))
            return JsonResponse({
                'created': created,
                'task': map_delayed_run_task(task)
            })
        elif request.data['type'] == 'Every':
            eta, seconds = parse_eta(flow)
            schedule, _ = IntervalSchedule.objects.get_or_create(every=seconds, period=IntervalSchedule.SECONDS)
            task, created = RepeatingRunTask.objects.get_or_create(
                user=user,
                interval=schedule,
                target=target,
                eta=eta,
                flow_owner=flow['repo']['owner']['login'],
                flow_name=flow['repo']['name'],
                name=f"User {user.username} flow {flow['repo']['name']} target {target.name} {schedule} repeating",
                task='plantit.runs.tasks.create_and_submit_run',
                args=json.dumps([user.username, target.name, flow]))
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
            'target': None,
            'created': None,
            'updated': None,
            'flow_owner': None,
            'flow_name': None,
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
    channel_layer = get_channel_layer()
    try:
        run = Run.objects.get(guid=id)
    except:
        return HttpResponseNotFound()

    if run.is_complete:
        return HttpResponse(f"Run {id} is no longer running")

    message = f"Attempting to cancel run {id}"
    if run.is_sandbox:
        # cancel the Celery task
        AsyncResult(run.submission_id).revoke()
        run.job_status = 'CANCELLED'
        run.updated = timezone.now()
        run.save()

        update_status(run, message)
        return HttpResponse(message)
    else:
        # cancel the cluster scheduler job
        cancel_job(run)
        run.job_status = 'CANCELLED'
        run.updated = timezone.now()
        run.save()

        update_status(run, message)
        return HttpResponse(message)


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


class RunConsumer(WebsocketConsumer):
    def connect(self):
        self.run_id = self.scope['url_route']['kwargs']['id']
        print(f"Socket connected for run {self.run_id}")
        async_to_sync(self.channel_layer.group_add)(self.run_id, self.channel_name)
        self.accept()

    def disconnect(self, code):
        print(f"Socket disconnected for run {self.run_id}")
        # async_to_sync(self.channel_layer.group_discard)(self.run_id, self.channel_name)

    def update_status(self, event):
        run = Run.objects.get(guid=self.run_id)
        print(f"Received status update for run {self.run_id} with status {run.job_status}")
        self.send(text_data=json.dumps({
            'run': map_run(run, True),
        }))
