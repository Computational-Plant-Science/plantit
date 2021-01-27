import binascii
import os
import tempfile
import uuid
from os.path import join
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse, FileResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from plantit import settings
from plantit.runs.models import Run, Status
from plantit.runs.ssh import SSH
from plantit.runs.thumbnail import Thumbnail
from plantit.runs.utils import execute, cleanup
from plantit.targets.models import Target
from plantit.utils import get_repo_config


@api_view(['GET'])
@login_required
def get_runs_by_user(request, username, page):
    start = int(page) * 20
    count = start + 20

    try:
        user = User.objects.get(username=username)
        runs = Run.objects.filter(user=user).order_by('-created')[start:(start + count)]
        return JsonResponse([{
            'id': run.identifier,
            'work_dir': run.work_dir,
            'target': run.target.name,
            'created': run.created,
            'started': run.started,
            'timeout': run.timeout,
            'updated': run.status.date if run.status is not None else run.created,
            'state': run.status.state if run.status is not None else 'Unknown',
            'description': run.status.description if run.status is not None else '',
            'flow_owner': run.flow_owner,
            'flow_name': run.flow_name,
            'tags': [str(tag) for tag in run.tags.all()]
        } for run in runs], safe=False)
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
        run = Run.objects.get(identifier=id)
        flow_config = get_repo_config(run.flow_name, run.flow_owner, run.user.profile.github_token)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    included_by_name = ((flow_config['output']['include']['names'] if 'names' in flow_config['output']['include'] else []) + [f"{run.identifier}.zip"]) if 'output' in flow_config else []
    included_by_pattern = (flow_config['output']['include']['patterns'] if 'patterns' in flow_config['output']['include'] else []) if 'output' in flow_config else []

    included_by_name.append(f"{run.identifier}.log")

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
        run = Run.objects.get(identifier=id)
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

            run_dir = join(settings.MEDIA_ROOT, run.identifier)
            thumbnail_path = join(run_dir, file)
            thumbnail_name_lower = file.lower()

            # make thumbnail directory for this run if it does not already exist
            Path(run_dir).mkdir(exist_ok=True, parents=True)

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
        run = Run.objects.get(identifier=id)
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
def get_logs_text(request, id, size):
    try:
        run = Run.objects.get(identifier=id)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    client = SSH(run.target.hostname, run.target.port, run.target.username)
    work_dir = join(run.target.workdir, run.work_dir)
    log_file = f"{run.identifier}.log"

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
def get_logs(request, id):
    try:
        run = Run.objects.get(identifier=id)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    client = SSH(run.target.hostname, run.target.port, run.target.username)
    work_dir = join(run.target.workdir, run.work_dir)
    log_file = f"{run.identifier}.log"

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


@api_view(['GET', 'POST'])
@login_required
def runs(request):
    if request.method == 'GET':
        runs = Run.objects.all()
        return JsonResponse([{
            'id': run.identifier,
            'work_dir': run.work_dir,
            'target': run.target.name,
            'created': run.created,
            'started': run.started,
            'timeout': run.timeout,
            'updated': run.status.date if run.status is not None else run.created,
            'state': run.status.state if run.status is not None else 'Unknown',
            'description': run.status.description if run.status is not None else '',
            'flow_owner': run.flow_owner,
            'flow_name': run.flow_name,
            'tags': [str(tag) for tag in run.tags.all()]
        } for run in runs], safe=False)

    elif request.method == 'POST':
        user = request.user
        flow = request.data
        now = timezone.now()
        now_str = now.strftime('%s')
        target = Target.objects.get(name=flow['config']['target']['name'])
        flow_path = f"{flow['repo']['owner']['login']}/{flow['repo']['name']}"
        print(flow['config']['tags'])
        run = Run.objects.create(
            user=User.objects.get(username=user.username),
            flow_owner=flow['repo']['owner']['login'],
            flow_name=flow['repo']['name'],
            target=target,
            created=now,
            work_dir=now_str + "/",
            remote_results_path=now_str + "/",
            identifier=uuid.uuid4(),
            token=binascii.hexlify(os.urandom(20)).decode())

        for tag in flow['config']['tags']:
            run.tags.add(tag)

        run.status_set.create(description=f"Creating run '{run.identifier}'",
                              state=Status.CREATING,
                              location='PlantIT')
        run.save()

        config = {
            'identifier': run.identifier,
            'workdir': join(target.workdir, now_str),
            'image': flow['config']['image'],
            'command': flow['config']['commands'],
            'parameters': flow['config']['params'],
            'target': flow['config']['target'],
            'log_file': f"{run.identifier}.log",
        }

        if 'gpu' in flow['config']:
            config['gpu'] = flow['config']['gpu']
        if 'branch' in flow['config']:
            config['branch'] = flow['config']['branch']
        if 'mount' in flow['config']:
            config['mount'] = flow['config']['mount']
        if 'input' in flow['config']:
            config['input'] = flow['config']['input']
        if 'output' in flow['config']:
            flow['config']['output']['from'] = join(target.workdir, run.work_dir, flow['config']['output']['from'])
            config['output'] = flow['config']['output']

        from plantit.celery import app
        if 'resources' in flow['config']['target']:
            time_split = flow['config']['target']['resources']['time'].split(':')
            time_hours = int(time_split[0])
            time_minutes = int(time_split[1])
            time_seconds = int(time_split[2])
            time_limit_seconds = time_seconds + 60 * time_minutes + 60 * time_hours * 2  # twice the given walltime, to allow for scheduler delay
        else:
            time_limit_seconds = 600  # otherwise just default to 10 minutes
        app.control.time_limit('plantit.runs.utils.execute', soft=time_limit_seconds)
        run.timeout = time_limit_seconds
        run.save()

        # start the run now
        task = execute.delay({
            'repo': flow['repo'],
            'config': config
        }, run.identifier, run.token, request.user.profile.cyverse_token)

        # schedule a cleanup task to run after the timeout
        cleanup.s(task.id, run.identifier, run.token, request.user.profile.cyverse_token).apply_async(countdown=run.timeout)

        return JsonResponse({
            'id': run.identifier
        })


@api_view(['GET'])
@login_required
def run(request, id):
    try:
        run = Run.objects.get(identifier=id)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    return JsonResponse({
        'id': run.identifier,
        'work_dir': run.work_dir,
        'target': run.target.name,
        'created': run.created,
        'started': run.started,
        'timeout': run.timeout,
        'updated': run.status.date if run.status is not None else run.created,
        'state': run.status.state if run.status is not None else 'Unknown',
        'description': run.status.description if run.status is not None else '',
        'flow_owner': run.flow_owner,
        'flow_name': run.flow_name,
        'tags': [str(tag) for tag in run.tags.all()]
    })


@api_view(['GET', 'POST'])
@login_required
@csrf_exempt
def status(request, id):
    if request.method == 'GET':
        try:
            run = Run.objects.get(identifier=id)
            return JsonResponse([
                {
                    'run_id': id,
                    'state': status.state,
                    'location': status.location,
                    'date': status.date,
                    'description': status.description
                } for status in list(run.status_set.all())], safe=False)
        except Run.DoesNotExist:
            return HttpResponseNotFound()

    elif request.method == 'POST':
        status = request.data
        state = int(status['state'])

        # FAILED = 0
        # CREATED = 1
        # PULLING = 2
        # RUNNING = 3
        # ZIPPING = 4
        # PUSHING = 5
        # COMPLETED = 6

        if state == 0 or 'error' in status['description'].lower():
            pass  # state == Status.FAILED
        if state == 1:
            state = Status.CREATING
        elif state == 2:
            state = Status.PULLING
        elif state == 3:
            state = Status.RUNNING
        elif state == 4:
            state = Status.ZIPPING
        elif state == 5:
            state = Status.PUSHING
        elif state == 6:
            state = Status.COMPLETED
        else:
            raise ValueError(f"Invalid value for state '{status['state']}' (expected 0 - 6)")

        try:
            run = Run.objects.get(identifier=id)
        except Run.DoesNotExist:
            return HttpResponseNotFound()

        for chunk in status['description'].split('<br>'):
            for line in chunk.split('\n'):
                if 'old time stamp' in line or 'image path' in line or 'Cache folder' in line or line == '':
                    continue
                run.status_set.create(description=line, state=state, location=run.target.name)

        run.save()
        return HttpResponse(status=200)
