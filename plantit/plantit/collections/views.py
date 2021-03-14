import json
import uuid

import httpx
import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseNotFound, HttpResponseBadRequest, JsonResponse
from django.utils import timezone
from rest_framework.decorators import api_view

from plantit.notifications.models import DirectoryPolicyNotification
from plantit.collections.models import CollectionAccessPolicy, CollectionRole
from plantit.collections.utils import map_collection_policy


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
