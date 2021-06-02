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
from plantit.submissions.models import Submission, DelayedSubmissionTask, RepeatingSubmissionTask, SubmissionStatus
from plantit.tasks import submit_workflow
from plantit.submissions.utils import update_submission_status, map_submission, get_submission_log_file_path, create_submission, parse_eta, \
    map_delayed_submission_task, \
    map_repeating_submission_task, cancel_submission
from plantit.ssh import SSH


@api_view(['GET', 'POST'])
@login_required
def get_all_or_create(request):
    user = request.user
    workflow = request.data

    if request.method == 'GET':
        submissions = Submission.objects.all()
        return JsonResponse({'submissions': [map_submission(sub) for sub in submissions]})
    elif request.method == 'POST':
        agent = Agent.objects.get(name=workflow['config']['agent']['name'])
        if request.data['type'] == 'Now':
            submission = create_submission(user.username, agent.name, workflow, workflow['config'].get('submission_name', None))
            submit_workflow.delay(submission.guid, workflow)
            return JsonResponse({'name': submission.name, 'owner': submission.user.username})
        elif request.data['type'] == 'After':
            eta, seconds = parse_eta(workflow)
            schedule, _ = IntervalSchedule.objects.get_or_create(every=seconds, period=IntervalSchedule.SECONDS)
            task, created = DelayedSubmissionTask.objects.get_or_create(
                user=user,
                interval=schedule,
                agent=agent,
                eta=eta,
                one_off=True,
                workflow_owner=workflow['repo']['owner']['login'],
                workflow_name=workflow['repo']['name'],
                name=f"User {user.username} workflow {workflow['repo']['name']} agent {agent.name} {schedule} once",
                task='plantit.tasks.create_and_submit_workflow',
                args=json.dumps([user.username, agent.name, workflow]))
            return JsonResponse({
                'created': created,
                'task': map_delayed_submission_task(task)
            })
        elif request.data['type'] == 'Every':
            eta, seconds = parse_eta(workflow)
            schedule, _ = IntervalSchedule.objects.get_or_create(every=seconds, period=IntervalSchedule.SECONDS)
            task, created = RepeatingSubmissionTask.objects.get_or_create(
                user=user,
                interval=schedule,
                agent=agent,
                eta=eta,
                workflow_owner=workflow['repo']['owner']['login'],
                workflow_name=workflow['repo']['name'],
                name=f"User {user.username} workflow {workflow['repo']['name']} agent {agent.name} {schedule} repeating",
                task='plantit.tasks.create_and_submit_workflow',
                args=json.dumps([user.username, agent.name, workflow]))
            return JsonResponse({
                'created': created,
                'task': map_repeating_submission_task(task)
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

    submissions = Submission.objects.filter(user=user)

    if 'running' in params and params.get('running') == 'True':
        submissions = [sub for sub in submissions.filter(completed__isnull=True).order_by('-created') if not sub.is_complete]
    elif 'running' in params and params.get('running') == 'False':
        submissions = [sub for sub in submissions if sub.is_complete]
        if page > -1:
            start = int(page) * 20
            count = start + 20
            submissions = submissions[start:(start + count)]
    else:
        if page > -1:
            start = int(page) * 20
            count = start + 20
            submissions = submissions[start:(start + count)]

    return JsonResponse({'submissions': [map_submission(sub) for sub in submissions]})


@api_view(['GET'])
@login_required
def get_by_owner_and_name(request, owner, name):
    try:
        user = User.objects.get(username=owner)
        submission = Submission.objects.get(user=user, name=name)
        return JsonResponse(map_submission(submission))
    except Submission.DoesNotExist:
        return HttpResponseNotFound()


@api_view(['GET'])
@login_required
def get_thumbnail(request, owner, name):
    path = request.GET.get('path')
    file = path.rpartition('/')[2]

    try:
        user = User.objects.get(username=owner)
        submission = Submission.objects.get(user=user, name=name)
    except:
        return HttpResponseNotFound()

    redis = RedisClient.get()
    preview = redis.get(f"previews/{user.username}/{submission.name}/{file}")

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
def get_3d_model(request, guid):
    path = request.GET.get('path')
    file = path.rpartition('/')[2]

    try:
        submission = Submission.objects.get(guid=guid)
    except:
        return HttpResponseNotFound()

    client = SSH(submission.agent.hostname, submission.agent.port, submission.agent.username)
    work_dir = join(submission.agent.workdir, submission.workdir)

    with tempfile.NamedTemporaryFile() as temp_file:
        with client:
            with client.client.open_sftp() as sftp:
                sftp.chdir(work_dir)
                sftp.get(file, temp_file.name)
        return HttpResponse(temp_file, content_type="applications/octet-stream")


@api_view(['GET'])
@login_required
def get_output_file(request, owner, name, file):
    try:
        user = User.objects.get(username=owner)
        submission = Submission.objects.get(user=user, name=name)
    except Submission.DoesNotExist:
        return HttpResponseNotFound()

    client = SSH(submission.agent.hostname, submission.agent.port, submission.agent.username)
    work_dir = join(submission.agent.workdir, submission.workdir)

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
        submission = Submission.objects.get(user=user, name=name)
    except Submission.DoesNotExist:
        return HttpResponseNotFound()

    log_path = get_submission_log_file_path(submission)
    return FileResponse(open(log_path, 'rb')) if Path(log_path).is_file() else HttpResponseNotFound()


@api_view(['GET'])
@login_required
def get_container_logs(request, owner, name):
    try:
        user = User.objects.get(username=owner)
        submission = Submission.objects.get(user=user, name=name)
    except Submission.DoesNotExist:
        return HttpResponseNotFound()

    client = SSH(submission.agent.hostname, submission.agent.port, submission.agent.username)
    work_dir = join(submission.agent.workdir, submission.workdir)

    if submission.agent.launcher:
        log_file = f"plantit.{submission.job_id}.out"
    else:
        log_file = f"{user.username}.{submission.name}.{submission.agent.name.lower()}.log"

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
        submission = Submission.objects.get(user=user, name=name)
    except Submission.DoesNotExist:
        return HttpResponseNotFound()

    client = SSH(submission.agent.hostname, submission.agent.port, submission.agent.username)
    work_dir = join(submission.agent.workdir, submission.workdir)

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
        task = DelayedSubmissionTask.objects.get(name=task_name)
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

    task = RepeatingSubmissionTask.objects.get(name=task_name)
    task.enabled = not task.enabled
    task.save()
    return JsonResponse(map_repeating_submission_task(task))


@api_view(['GET'])
@login_required
def remove_repeating(request, owner, workflow_name):
    task_name = request.GET.get('name', None)
    if task_name is None:
        return HttpResponseNotFound()

    try:
        task = RepeatingSubmissionTask.objects.get(name=task_name)
    except:
        return HttpResponseNotFound()

    task.delete()
    return JsonResponse({'deleted': True})


@api_view(['GET'])
@login_required
def cancel(request, owner, name):
    try:
        user = User.objects.get(username=owner)
        submission = Submission.objects.get(user=user, name=name)
    except:
        return HttpResponseNotFound()

    if submission.is_complete:
        return HttpResponse(f"User {owner}'s submission {name} already completed")

    if submission.is_sandbox:
        AsyncResult(submission.celery_task_id).revoke()  # cancel the Celery task
    else:
        cancel_submission(submission)  # cancel the scheduler job

    now = timezone.now()
    submission.status = SubmissionStatus.CANCELED
    submission.updated = now
    submission.completed = now
    submission.save()

    msg = f"Cancelled user {owner}'s submission {name}"
    update_submission_status(submission, msg)
    return JsonResponse({'canceled': True})


@api_view(['GET'])
@login_required
def delete(request, owner, name):
    try:
        user = User.objects.get(username=owner)
        submission = Submission.objects.get(user=user, name=name)
    except:
        return HttpResponseNotFound()

    try:
        submission.delete()
        return JsonResponse({'deleted': True})
    except:
        return JsonResponse({'deleted': False})


@api_view(['GET'])
@login_required
def exists(request, owner, name):
    try:
        Submission.objects.get(user=User.objects.get(username=owner), name=name)
        return JsonResponse({'exists': True})
    except Submission.DoesNotExist:
        return JsonResponse({'exists': True})


@api_view(['POST'])
@login_required
@csrf_exempt
def status(request, owner, name):
    try:
        user = User.objects.get(username=owner)
        submission = Submission.objects.get(user=user, name=name)
    except Submission.DoesNotExist:
        return HttpResponseNotFound()

    for chunk in request.data['description'].split('<br>'):
        submission.status = SubmissionStatus.RUNNING
        for line in chunk.split('\n'):
            if 'FATAL' in line or int(request.data['state']) == 0:  # catch singularity build failures etc
                submission.status = SubmissionStatus.FAILURE
            elif int(request.data['state']) == 6:  # catch completion
                submission.status = SubmissionStatus.SUCCESS

            submission.updated = timezone.now()
            submission.save()
            update_submission_status(submission, line)

        submission.updated = timezone.now()
        submission.save()

    return HttpResponse(status=200)


@api_view(['GET'])
@login_required
def search(request, owner, workflow_name, page):
    try:
        user = User.objects.get(username=owner)
        start = int(page) * 20
        count = start + 20
        submissions = Submission.objects.filter(user=user, workflow_name=workflow_name).order_by('-created')[start:(start + count)]
        return JsonResponse([map_submission(sub) for sub in submissions], safe=False)
    except:
        return HttpResponseNotFound()


@api_view(['GET'])
@login_required
def search_delayed(request, owner, workflow_name):
    user = User.objects.get(username=owner)
    try:
        tasks = DelayedSubmissionTask.objects.filter(user=user)
    except:
        return HttpResponseNotFound()

    tasks = [task for task in tasks if task.workflow_name == workflow_name]
    return JsonResponse([map_delayed_submission_task(task) for task in tasks], safe=False)


@api_view(['GET'])
@login_required
def search_repeating(request, owner, workflow_name):
    user = User.objects.get(username=owner)
    try:
        tasks = RepeatingSubmissionTask.objects.filter(user=user)
    except:
        return HttpResponseNotFound()

    tasks = [task for task in tasks if task.workflow_name == workflow_name]
    return JsonResponse([map_repeating_submission_task(task) for task in tasks], safe=False)
