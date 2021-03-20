import binascii
import json
import os
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
        ssh_client = SSH(cluster.hostname, cluster.port, username, password)

    guid = str(uuid.uuid4())
    path = request.data['path']
    session = CollectionSession.objects.create(
        guid=guid,
        user=user,
        path=path,
        cluster=cluster,
        token=binascii.hexlify(os.urandom(20)).decode(),
        workdir=join(cluster.workdir, f"{guid}"))
    update_collection_session(session, [f"Creating working directory for collection session {session.guid} on {cluster.name}"])

    try:
        with ssh_client:
            print(execute_command(
                    ssh_client=ssh_client,
                    pre_command=':',
                    command=f"mkdir {guid}/",
                    directory=cluster.workdir))
    except:
        update_collection_session(session, [f"Failed to create working directory for collection session {session.guid} on {cluster.name}"])
        session.delete()

    open_collection_session.s(session.guid).apply_async()

    # update_collection_session(session, [f"Opening collection {session.path} on {cluster.name} in working directory {join(session.cluster.workdir, session.workdir)}"])
    return JsonResponse({'session': map_collection_session(session)})


@api_view(['GET'])
@login_required
def close_session(request):
    user = request.user
    try:
        session = CollectionSession.objects.get(user=user)
    except:
        return HttpResponseNotFound()

    update_collection_session(session, [f"Closing collection session on {session.cluster.name}"])

    ssh_client = SSH(session.cluster.hostname, session.cluster.port, session.cluster.username)
    with ssh_client:
        output = execute_command(
                ssh_client=ssh_client,
                pre_command=':',
                command=f"rm -r {session.guid}/",
                directory=session.cluster.workdir)
        update_collection_session(session, output)

    session.delete()
    return HttpResponse()


@api_view(['GET'])
@login_required
def get_thumbnail(request, path):
    user = request.user
    try:
        session = CollectionSession.objects.get(user=user)
    except:
        return HttpResponseNotFound()


    thumbnail_name = path.rpartition('/')[2]
    thumbnail_path = join(os.environ.get('SESSIONS_LOGS'), thumbnail_name)
    file = requests.get(f"https://de.cyverse.org/terrain/secured/fileio/download?path={path}",
                        headers={'Authorization': f"Bearer {user.profile.cyverse_token}"}).content

    if thumbnail_name.endswith('txt') or thumbnail_name.endswith('csv') or thumbnail_name.endswith('yml') or thumbnail_name.endswith('yaml') or thumbnail_name.endswith('tsv') or thumbnail_name.endswith('out') or thumbnail_name.endswith('err') or thumbnail_name.endswith('log'):
        return HttpResponse(file, content_type='text/plain')

    return HttpResponse(file, content_type="image/jpg")