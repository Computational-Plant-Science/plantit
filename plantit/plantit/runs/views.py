import binascii
import os
import uuid
from os.path import join

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse, FileResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from plantit.runs.models import Run, Status
from plantit.runs.ssh import SSH
from plantit.runs.utils import execute
from plantit.targets.models import Target


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
            'updated': run.status.date if run.status is not None else run.created,
            'state': run.status.state if run.status is not None else 'Unknown',
            'description': run.status.description if run.status is not None else '',
            'flow_owner': run.flow_owner,
            'flow_name': run.flow_name
        } for run in runs], safe=False)
    except:
        return HttpResponseNotFound()


@api_view(['GET'])
def get_total_count(request):
    runs = Run.objects.all()
    return JsonResponse({'count': len(runs)})


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

            sftp.chdir(work_dir)
            sftp.get(log_file, log_file)
            with open(log_file, 'r') as file:
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

            sftp.chdir(work_dir)
            sftp.get(log_file, log_file)
            return FileResponse(open(log_file, 'rb'))




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
            'updated': run.status.date if run.status is not None else run.created,
            'state': run.status.state if run.status is not None else 'Unknown',
            'description': run.status.description if run.status is not None else '',
            'flow_owner': run.flow_owner,
            'flow_name': run.flow_name
        } for run in runs], safe=False)

    elif request.method == 'POST':
        user = request.user
        flow = request.data
        now = timezone.now()
        now_str = now.strftime('%s')
        target = Target.objects.get(name=flow['config']['target']['name'])
        flow_path = f"{flow['repo']['owner']['login']}/{flow['repo']['name']}"
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

        run.status_set.create(description=f"Creating run '{run.identifier}'",
                              state=Status.CREATED,
                              location='PlantIT')
        run.save()

        config = {
            'identifier': run.identifier,
            'api_url': os.environ['DJANGO_API_URL'] + f"runs/{run.identifier}/status/",
            'workdir': join(target.workdir, now_str),
            'clone': f"https://github.com/{flow_path}" if flow['config']['clone'] else None,
            'image': flow['config']['image'],
            'command': flow['config']['commands'],
            'params': flow['config']['params'],
            'target': flow['config']['target'],
            'logging': {
                'file': f"{run.identifier}.log"
            },
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
            print(flow['config']['output']['from'])
            config['output'] = flow['config']['output']

        execute.delay({
            'repo': flow['repo'],
            'config': config
        }, run.identifier, run.token, request.user.profile.cyverse_token)  # request.session._session['csrfToken']

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
        'updated': run.status.date if run.status is not None else run.created,
        'state': run.status.state if run.status is not None else 'Unknown',
        'description': run.status.description if run.status is not None else '',
        'flow_owner': run.flow_owner,
        'flow_name': run.flow_name
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

        if state == 1:
            state = Status.COMPLETED
        elif state == 2 or 'error' in status['description'].lower():
            state = Status.FAILED
        elif state == 3:
            state = Status.RUNNING
        elif state == 4:
            state = Status.CREATED
        else:
            raise ValueError(f"Invalid value for state '{status['state']}' (expected 1 - 4)")

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
