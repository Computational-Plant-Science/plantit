import binascii
import json
import os
import tempfile
import uuid
from os.path import join

import httpx
import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseNotFound, HttpResponseBadRequest, JsonResponse, HttpResponse
from django.utils import timezone
from rest_framework.decorators import api_view
from preview_generator.manager import PreviewManager
import czifile
import cv2

from plantit import settings
from plantit.clusters.models import Cluster, ClusterAccessPolicy, ClusterRole
from plantit.notifications.models import DirectoryPolicyNotification
from plantit.collections.models import CollectionAccessPolicy, CollectionRole, CollectionSession
from plantit.collections.utils import map_collection_policy, map_collection_session, update_collection_session
from plantit.runs.ssh import SSH
from plantit.runs.utils import execute_command
from plantit.runs.tasks import open_collection_session


@login_required
def sharing(request):  # directories the current user is sharing
    owner = request.user
    policies = CollectionAccessPolicy.objects.filter(owner=owner)
    return JsonResponse([map_collection_policy(policy) for policy in policies], safe=False)


@login_required
def shared(request):  # directories shared with the current user
    guest = request.user
    policies = CollectionAccessPolicy.objects.filter(guest=guest)

    urls = [f"https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path={policy.path}" for policy in policies]
    headers = {
        "Authorization": f"Bearer {guest.profile.cyverse_token}",
    }
    with httpx.Client(headers=headers) as client:
        responses = [client.get(url).json() for url in urls]
        # responses = asyncio.run(asyncio.gather(*futures))
        return JsonResponse([directory for directory in responses], safe=False)


@api_view(['POST'])
@login_required
def share(request):
    owner = request.user
    guests = request.data['sharing']
    policies = []

    for guest in guests:
        try:
            user = User.objects.get(username=guest['user'])
        except:
            return HttpResponseNotFound()

        path = guest['paths'][0]['path']
        role = CollectionRole.read if guest['paths'][0]['permission'].lower() == 'read' else CollectionRole.write
        policy, created = CollectionAccessPolicy.objects.get_or_create(owner=owner, guest=user, role=role, path=path)
        policies.append({
            'created': created,
            'policy': map_collection_policy(policy)
        })

        notification = DirectoryPolicyNotification.objects.create(
            guid=str(uuid.uuid4()),
            user=user,
            created=timezone.now(),
            policy=policy,
            message=f"{owner.username} shared directory {policy.path} with you")
        async_to_sync(get_channel_layer().group_send)(f"notifications-{user.username}", {
            'type': 'push_notification',
            'notification': {
                'id': notification.guid,
                'username': notification.user.username,
                'created': notification.created.isoformat(),
                'message': notification.message,
                'read': notification.read,
                'policy': map_collection_policy(notification.policy)
            }
        })

    response = requests.post("https://de.cyverse.org/terrain/secured/share",
                             data=json.dumps(request.data),
                             headers={"Authorization": f"Bearer {owner.profile.cyverse_token}", "Content-Type": 'application/json;charset=utf-8'})
    response.raise_for_status()

    return JsonResponse({'policies': policies})


@api_view(['POST'])
@login_required
def unshare(request):
    owner = request.user
    guest_username = request.data['user']
    path = request.data['path']
    role_str = str(request.data['role'])

    if role_str.lower() != 'read' and role_str.lower() != 'write':
        return HttpResponseBadRequest(f"Unsupported role {role_str} (allowed: read, write)")
    else:
        role = CollectionRole.read if role_str.lower() == 'read' else CollectionRole.write

    try:
        guest = User.objects.get(username=guest_username)
    except:
        return HttpResponseNotFound()

    try:
        policy = CollectionAccessPolicy.objects.get(owner=owner, guest=guest, role=role, path=path)
    except:
        return HttpResponseNotFound()

    notification = DirectoryPolicyNotification.objects.create(
        guid=str(uuid.uuid4()),
        user=guest,
        created=timezone.now(),
        policy=policy,
        message=f"{owner.username} revoked your access to directory {policy.path}")
    async_to_sync(get_channel_layer().group_send)(f"notifications-{guest.username}", {
        'type': 'push_notification',
        'notification': {
            'id': notification.guid,
            'username': notification.user.username,
            'created': notification.created.isoformat(),
            'message': notification.message,
            'read': notification.read,
            'policy': map_collection_policy(notification.policy)
        }
    })

    response = requests.post("https://de.cyverse.org/terrain/secured/unshare",
                             data=json.dumps({
                                 'unshare': [{
                                     'user': path,
                                     'paths': [path]
                                 }]
                             }),
                             headers={"Authorization": f"Bearer {owner.profile.cyverse_token}", "Content-Type": 'application/json;charset=utf-8'})
    response.raise_for_status()
    policy.delete()

    return JsonResponse({'unshared': True})


@api_view(['GET'])
@login_required
def opened_session(request):
    user = request.user
    try:
        session = CollectionSession.objects.get(user=user)
    except:
        return HttpResponseNotFound()
    return JsonResponse({'session': map_collection_session(session)})


@api_view(['POST'])
@login_required
def open_session(request):
    user = request.user
    try:
        CollectionSession.objects.get(user=user)
        return HttpResponseBadRequest(f"Collection session already running")
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

    guid = str(uuid.uuid4())
    path = request.data['path']
    session = CollectionSession.objects.create(
        guid=guid,
        user=user,
        path=path,
        cluster=cluster,
        token=binascii.hexlify(os.urandom(20)).decode(),
        workdir=join(cluster.workdir, f"{guid}"))

    open_collection_session.s(session.guid).apply_async(countdown=5)
    update_collection_session(session, [f"Opening collection {session.path} on {cluster.name} in working directory {join(session.cluster.workdir, session.workdir)}"])
    return JsonResponse({'session': map_collection_session(session)})


@api_view(['GET'])
@login_required
def save_session(request):
    user = request.user
    try:
        session = CollectionSession.objects.get(user=user)
    except:
        return HttpResponseNotFound()

    if session.save_task_id is not None:
        return JsonResponse({'saved': False})




@api_view(['GET'])
@login_required
def close_session(request):
    user = request.user
    try:
        session = CollectionSession.objects.get(user=user)
    except:
        return HttpResponseNotFound()

    update_collection_session(session, [f"Closing collection session {session.guid}"])

    ssh_client = SSH(session.cluster.hostname, session.cluster.port, session.cluster.username)
    with ssh_client:
        with ssh_client.client.open_sftp() as sftp:
            try:
                sftp.stat(join(session.cluster.workdir, session.guid))
                execute_command(
                    ssh_client=ssh_client,
                    pre_command=':',
                    command=f"rm -r {session.guid}/",
                    directory=session.cluster.workdir)
                update_collection_session(session, [f"Removed collection session {session.guid} working directory {session.workdir}"])
            except:
                update_collection_session(session, [f"Directory {session.guid} does not exist, skipping"])

    session.delete()
    return HttpResponse()


@api_view(['GET'])
@login_required
def get_text_content(request):
    user = request.user
    try:
        session = CollectionSession.objects.get(user=user)
    except:
        return HttpResponseNotFound()

    path = request.GET.get('path')
    file_name = path.rpartition('/')[2]
    file = join(session.workdir, file_name)
    client = SSH(session.cluster.hostname, session.cluster.port, session.cluster.username)

    with client:
        with client.client.open_sftp() as sftp:
            stdin, stdout, stderr = client.client.exec_command(f"test -e {join(session.workdir, file)} && echo exists")
            errs = stderr.read()
            if errs:
                raise Exception(f"Failed to check existence of {file}: {errs}")

            if file.endswith('txt') or \
                    file.endswith('csv') or \
                    file.endswith('yml') or \
                    file.endswith('yaml') or \
                    file.endswith('tsv') or \
                    file.endswith('out') or \
                    file.endswith('err') or \
                    file.endswith('log'):
                with tempfile.NamedTemporaryFile() as temp_file:
                    sftp.chdir(session.workdir)
                    sftp.get(file, temp_file.name)
                    with open(temp_file.name, 'r') as file:
                        lines = file.readlines()
                        return HttpResponse(lines, content_type='text/plain')


@api_view(['GET'])
@login_required
def get_thumbnail(request):
    user = request.user
    try:
        session = CollectionSession.objects.get(user=user)
    except:
        return HttpResponseNotFound()

    path = request.GET.get('path')
    file_name = path.rpartition('/')[2]
    file = join(session.workdir, file_name)
    client = SSH(session.cluster.hostname, session.cluster.port, session.cluster.username)

    with client:
        with client.client.open_sftp() as sftp:
            stdin, stdout, stderr = client.client.exec_command(f"test -e {join(session.workdir, file)} && echo exists")
            errs = stderr.read()
            if errs:
                raise Exception(f"Failed to check existence of {file}: {errs}")

            manager = PreviewManager(join(settings.MEDIA_ROOT, session.guid), create_folder=True)

            if file.endswith('txt') or \
                    file.endswith('csv') or \
                    file.endswith('yml') or \
                    file.endswith('yaml') or \
                    file.endswith('tsv') or \
                    file.endswith('out') or \
                    file.endswith('err') or \
                    file.endswith('log'):
                with tempfile.NamedTemporaryFile() as temp_file:
                    sftp.chdir(session.workdir)
                    sftp.get(file, temp_file.name)
                    preview_file = manager.get_jpeg_preview(temp_file.name, width=1024, height=1024)
                    with open(preview_file, 'rb') as preview:
                        return HttpResponse(preview, content_type="image/jpg")
            # elif file.endswith('ply'):
            #     with tempfile.NamedTemporaryFile() as temp_file:
            #         print(f"Creating preview for {file_name}")
            #         sftp.chdir(session.workdir)
            #         sftp.get(file, temp_file.name)
            #         preview = manager.get_jpeg_preview(temp_file.name)
            #         with open(preview, 'rb') as preview_file:
            #             return HttpResponse(preview_file, content_type="image/jpg")
            elif file.endswith('png') or file.endswith('jpg') or file.endswith('jpeg'):
                with tempfile.NamedTemporaryFile() as temp_file:
                    print(f"Creating thumbnail for {file_name}")
                    sftp.chdir(session.workdir)
                    sftp.get(file, temp_file.name)
                    return HttpResponse(temp_file, content_type="image/png")
            elif file.endswith('czi'):
                with tempfile.NamedTemporaryFile() as temp_file:
                    print(f"Creating thumbnail for {file_name}")
                    sftp.chdir(session.workdir)
                    sftp.get(file, temp_file.name)
                    image = czifile.imread(temp_file.name)
                    image.shape = (image.shape[2], image.shape[3], image.shape[4])
                    success, buffer = cv2.imencode(".jpg", image)
                    buffer.tofile(temp_file.name)
                    return HttpResponse(temp_file, content_type="image/png")
            elif file.endswith('ply'):
                with tempfile.NamedTemporaryFile() as temp_file:
                    sftp.chdir(session.workdir)
                    sftp.get(file, temp_file.name)
                    # preview = manager.get_jpeg_preview(temp_file.name, width=200, height=200)
                    # with open(preview, 'rb') as preview_file:
                    #     return HttpResponse(preview_file, content_type="image/jpg")
                    return HttpResponse(temp_file, content_type="applications/octet-stream")

            # if file.endswith('txt') or file.endswith('csv') or file.endswith('yml') or file.endswith('yaml') or file.endswith('tsv') or file.endswith('out') or file.endswith('err') or file.endswith('log'):
            #     with tempfile.NamedTemporaryFile() as temp_file:
            #         sftp.chdir(session.workdir)
            #         sftp.get(file, temp_file.name)
            #         with tempfile.NamedTemporaryFile() as tf:
            #             sftp.chdir(session.workdir)
            #             sftp.get(file, tf.name)
            #             with open(tf.name, 'r') as file:
            #                 lines = file.readlines()
            #                 return HttpResponse(lines, content_type='text/plain')

            # if Path(thumbnail_path).exists():
            #     print(f"Using existing thumbnail: {thumbnail_path}")
            #     return redirect(thumbnail_path)
            #     # thumbnail = open(thumbnail_path, 'rb')
            # else:
            #     with tempfile.NamedTemporaryFile() as temp_file, open(thumbnail_path, 'wb') as thumbnail_file:
            #         print(f"Creating new thumbnail: {thumbnail_path}")
            #         sftp.chdir(session.workdir)
            #         sftp.get(file, temp_file.name)
            #         thumbnail = Thumbnail(source=temp_file).generate()
            #         thumbnail_file.write(thumbnail.read())

            # if thumbnail_name_lower.endswith('png'):
            #     return HttpResponse(thumbnail, content_type="image/png")
            # elif thumbnail_name_lower.endswith('jpg') or thumbnail_name_lower.endswith('jpeg'):
            #     return HttpResponse(thumbnail, content_type="image/jpg")
            # else:
            #     return HttpResponseNotFound()


@api_view(['POST'])
@login_required
def duplicate_file(request):
    user = request.user
    file = request.data['file']
    try:
        session = CollectionSession.objects.get(user=user)
    except:
        return HttpResponseNotFound()

    update_collection_session(session, [f"Duplicating file {file}"])

    if file not in session.modified:
        session.modified.append(file)
        session.save()

    ssh_client = SSH(session.cluster.hostname, session.cluster.port, session.cluster.username)
    with ssh_client:
        output = execute_command(
            ssh_client=ssh_client,
            pre_command=':',
            command=f"cp {file} {timezone.now()}.{file}",
            directory=session.cluster.workdir)
        update_collection_session(session, output)

    return HttpResponse()
