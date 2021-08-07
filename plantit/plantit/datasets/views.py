import asyncio
import json
import traceback
import uuid
from typing import List

import httpx
import requests
from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseNotFound, HttpResponseBadRequest, JsonResponse
from django.utils import timezone

from plantit.datasets.models import DatasetAccessPolicy, DatasetRole
from plantit.miappe.models import Investigation, Study
from plantit.notifications.models import Notification
from plantit.utils import dataset_access_policy_to_dict, project_to_dict


@login_required
def sharing(request):  # directories the current user is sharing
    policies = DatasetAccessPolicy.objects.filter(owner=request.user)
    return JsonResponse({'datasets': [dataset_access_policy_to_dict(policy) for policy in policies]})


@sync_to_async
@login_required
@async_to_sync
async def shared(request):  # directories shared with the current user
    policies = await sync_to_async(list)(DatasetAccessPolicy.objects.filter(guest=request.user))
    urls = [f"https://de.cyverse.org/terrain/secured/filesystem/paged-directory?limit=1000&path={policy.path}" for policy in policies]
    headers = {
        "Authorization": f"Bearer {request.user.profile.cyverse_access_token}",
    }
    async with httpx.AsyncClient(headers=headers) as client:
        tasks = [client.get(url).json() for url in urls]
        results = await asyncio.gather(*tasks)
        return JsonResponse({'datasets': [directory for directory in results]})


@sync_to_async
@login_required
@async_to_sync
async def share(request):
    owner = request.user
    body = json.loads(request.body.decode('utf-8'))
    guests = body['sharing']
    policies = []

    for guest in guests:
        try:
            user = await sync_to_async(User.objects.get)(owner=guest['user'])
        except:
            print(traceback.format_exc())
            return HttpResponseNotFound()

        path = guest['paths'][0]['path']
        role = DatasetRole.read if guest['paths'][0]['permission'].lower() == 'read' else DatasetRole.write
        policy, created = await sync_to_async(DatasetAccessPolicy.objects.get_or_create)(owner=owner, guest=user, role=role, path=path)
        policies.append({
            'created': created,
            'policy': dataset_access_policy_to_dict(policy)
        })

        notification = await sync_to_async(Notification.objects.create)(
            guid=str(uuid.uuid4()),
            user=user,
            created=timezone.now(),
            message=f"{owner.username} shared directory {policy.path} with you")

        await get_channel_layer().group_send(f"notifications-{user.username}", {
            'type': 'push_notification',
            'notification': {
                'id': notification.guid,
                'username': notification.user.username,
                'created': notification.created.isoformat(),
                'message': notification.message,
                'read': notification.read,
                'policy': dataset_access_policy_to_dict(notification.policy)
            }
        })

    headers = {
        "Authorization": f"Bearer {request.user.profile.cyverse_access_token}",
    }
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.post("https://de.cyverse.org/terrain/secured/share", data=json.dumps(body))
        response.raise_for_status()

    return JsonResponse({'policies': policies})


@sync_to_async
@login_required
@async_to_sync
async def unshare(request):
    owner = request.user
    body = json.loads(request.body.decode('utf-8'))
    guest_username = body['user']
    path = body['path']
    role_str = str(body['role'])

    if role_str.lower() != 'read' and role_str.lower() != 'write':
        return HttpResponseBadRequest(f"Unsupported role {role_str} (allowed: read, write)")
    else:
        role = DatasetRole.read if role_str.lower() == 'read' else DatasetRole.write

    try:
        guest = await sync_to_async(User.objects.get)(owner=guest_username)
    except:
        return HttpResponseNotFound()

    try:
        policy = await sync_to_async(DatasetAccessPolicy.objects.get)(owner=owner, guest=guest, role=role, path=path)
    except:
        return HttpResponseNotFound()

    notification = await sync_to_async(Notification.objects.create)(
        guid=str(uuid.uuid4()),
        user=guest,
        created=timezone.now(),
        message=f"{owner.username} revoked your access to directory {policy.path}")

    await get_channel_layer().group_send(f"notifications-{guest.username}", {
        'type': 'push_notification',
        'notification': {
            'id': notification.guid,
            'username': notification.user.username,
            'created': notification.created.isoformat(),
            'message': notification.message,
            'read': notification.read,
            'policy': dataset_access_policy_to_dict(notification.policy)
        }
    })

    headers = {
        "Authorization": f"Bearer {request.user.profile.cyverse_access_token}",
        "Content-Type": 'application/json;charset=utf-8'
    }
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.post("https://de.cyverse.org/terrain/secured/unshare", data=json.dumps({'unshare': [{'user': path, 'paths': [path]}]}))
        response.raise_for_status()

    await sync_to_async(policy.delete)()
    return JsonResponse({'unshared': True})


@sync_to_async
@login_required
@async_to_sync
async def create(request):
    owner = request.user
    body = json.loads(request.body.decode('utf-8'))
    path = body['path']
    project = body.get('project', None)
    study = body.get('study', None)
    headers = {
        "Authorization": f"Bearer {request.user.profile.cyverse_access_token}",
    }
    async with httpx.AsyncClient(headers=headers) as client:
        response = await client.post("https://de.cyverse.org/terrain/secured/filesystem/directory/create", data=json.dumps({'path': path}))
        response.raise_for_status()

    if project is not None and study is not None:
        try:
            investigation = Investigation.objects.get(owner=owner, title=project)
            study = Study.objects.get(investigation=investigation, title=study)
            study.dataset_paths.append(path)
            study.save()
            return JsonResponse({'path': path, 'project': project_to_dict(investigation)})
        except:
            return HttpResponseNotFound()
    else:
        return JsonResponse({'path': path})