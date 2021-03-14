import binascii
import os
import tempfile
import uuid
from os.path import join
from pathlib import Path

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound, HttpResponse, HttpResponseBadRequest, JsonResponse
from rest_framework.decorators import api_view

from plantit import settings
from plantit.clusters.models import Cluster, ClusterAccessPolicy, ClusterRole
from plantit.runs.ssh import SSH
from plantit.runs.utils import execute_command
from plantit.sessions.models import Session
from plantit.sessions.utils import map_session, update_session


@api_view(['POST'])
@login_required
def start(request):
    user = request.user
    try:
        session = Session.objects.get(user=user)
        return HttpResponseBadRequest(f"User session already running")
    except:
        pass

    try:
        cluster_name = request.data['cluster']
        cluster = Cluster.objects.get(name=cluster_name)
    except:
        return HttpResponseNotFound()

    policies = ClusterAccessPolicy.objects.filter(user=user, role__in=[ClusterRole.own, ClusterRole.run])
    if len(policies) > 0:  # user already has guest or admin permissions
        ssh_client = SSH(cluster.hostname, cluster.port, cluster.username)
    else:  # authenticating manually
        if 'auth' not in request.data:
            return HttpResponseBadRequest(f"User not authorized; you must provide authentication information")
        username = request.data['auth']['username']
        password = request.data['auth']['password']
        ssh_client = SSH(cluster.hostname, cluster.port, username, password)

    guid = str(uuid.uuid4())
    session = Session.objects.create(
        guid=guid,
        user=user,
        cluster=cluster,
        token=binascii.hexlify(os.urandom(20)).decode(),
        workdir=f"{guid}/")
    update_session(session, [f"Creating session on {cluster.name}"])

    try:
        with ssh_client:
            print(execute_command(
                    ssh_client=ssh_client,
                    pre_command=':',
                    command=f"mkdir {guid}/",
                    directory=cluster.workdir))
    except:
        update_session(session, [f"Failed to create session on {cluster.name}"])
        session.delete()

    update_session(session, [f"Started session on {cluster.name} with working directory {session.workdir}"])
    return JsonResponse({'session': map_session(session)})


@api_view(['GET'])
@login_required
def stop(request):
    user = request.user
    try:
        session = Session.objects.get(user=user)
    except:
        return HttpResponseNotFound()

    update_session(session, [f"Closing interactive session on {session.cluster.name}"])

    ssh_client = SSH(session.cluster.hostname, session.cluster.port, session.cluster.username)
    with ssh_client:
        output = execute_command(
                ssh_client=ssh_client,
                pre_command=':',
                command=f"rm -r {session.guid}/",
                directory=session.cluster.workdir)
        update_session(session, output)

    session.delete()
    return HttpResponse()


@api_view(['GET'])
@login_required
def get(request):
    user = request.user
    try:
        session = Session.objects.get(user=user)
    except:
        return HttpResponseNotFound()
    return JsonResponse({'session': map_session(session)})


@api_view(['GET'])
@login_required
def get_thumbnail(request, id, file):
    try:
        run = Session.objects.get(guid=id)
    except Session.DoesNotExist:
        return HttpResponseNotFound()

    ssh = SSH(run.cluster.hostname, run.cluster.port, run.cluster.username)
    workdir = join(run.cluster.workdir, run.work_dir)

    with ssh:
        with ssh.client.open_sftp() as sftp:
            stdin, stdout, stderr = ssh.client.exec_command(f"test -e {join(workdir, file)} && echo exists")
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

                    sftp.chdir(workdir)
                    sftp.get(file, temp_file.name)

                    with tempfile.NamedTemporaryFile() as tf:
                        sftp.chdir(workdir)
                        sftp.get(file, tf.name)
                        with open(tf.name, 'r') as file:
                            lines = file.readlines()
                            return HttpResponse(lines, content_type='text/plain')

            with tempfile.NamedTemporaryFile() as temp_file, open(thumbnail_path, 'wb') as thumbnail_file:
                print(f"Creating new thumbnail: {thumbnail_path}")
                sftp.chdir(workdir)
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
                    sftp.chdir(workdir)
                    sftp.get(file, temp_file.name)
                    thumbnail = Thumbnail(source=temp_file).generate()
                    thumbnail_file.write(thumbnail.read())

            if thumbnail_name_lower.endswith('png'):
                return HttpResponse(thumbnail, content_type="image/png")
            elif thumbnail_name_lower.endswith('jpg') or thumbnail_name_lower.endswith('jpeg'):
                return HttpResponse(thumbnail, content_type="image/jpg")
            else:
                return HttpResponseNotFound()
