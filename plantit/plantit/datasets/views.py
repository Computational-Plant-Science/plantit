import json
import logging
import pprint
import traceback
import uuid

from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseNotFound, HttpResponseBadRequest, JsonResponse
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

import plantit.queries as q
import plantit.terrain as terrain
from plantit.datasets.models import DatasetAccessPolicy, DatasetRole
from plantit.miappe.models import Investigation, Study
from plantit.notifications.models import Notification
from plantit.users.models import Profile

logger = logging.getLogger(__name__)


# @swagger_auto_schema(methods='get')
@login_required
@api_view(['get'])
def sharing(request):
    """
    Get collections the current user is sharing.

    :param request: The request
    :return: The response
    """

    policies = DatasetAccessPolicy.objects.filter(owner=request.user)
    return JsonResponse({'datasets': [q.dataset_access_policy_to_dict(policy) for policy in policies]})


# @swagger_auto_schema(methods='get')
@sync_to_async
@login_required
@async_to_sync
@login_required
@api_view(['get'])
async def shared(request):
    """
    Get collections shared with the current user.

    :param request: The request
    :return: The response
    """

    policies = await sync_to_async(list)(DatasetAccessPolicy.objects.filter(guest=request.user))
    paths = [policy.path for policy in policies]
    dirs = await terrain.get_dirs_async(paths, request.user.profile.cyverse_access_token, int(settings.HTTP_TIMEOUT))
    return JsonResponse({'datasets': [dir for dir in dirs]})


@sync_to_async
@login_required
@async_to_sync
async def share(request):
    """
    Share a collection with another user.

    Args:
        request: The request

    Returns:

    """

    owner = request.user
    body = json.loads(request.body.decode('utf-8'))
    guests = body['sharing']
    policies = []

    for guest in guests:
        try:
            user = await sync_to_async(User.objects.get)(username=guest['user'])
        except:
            print(traceback.format_exc())
            return HttpResponseNotFound()

        path = guest['paths'][0]['path']
        role = DatasetRole.read if guest['paths'][0]['permission'].lower() == 'read' else DatasetRole.write
        policy, created = await sync_to_async(DatasetAccessPolicy.objects.get_or_create)(owner=owner, guest=user, role=role, path=path)
        policies.append({
            'created': created,
            'policy': await sync_to_async(q.dataset_access_policy_to_dict)(policy)
        })

        notification = await sync_to_async(Notification.objects.create)(
            guid=str(uuid.uuid4()),
            user=user,
            created=timezone.now(),
            message=f"{owner.username} shared directory {policy.path} with you")

        await get_channel_layer().group_send(f"{user.username}", {
            'type': 'push_notification',
            'notification': {
                'id': notification.guid,
                'username': notification.user.username,
                'created': notification.created.isoformat(),
                'message': notification.message,
                'read': notification.read,
            }
        })

    profile = await sync_to_async(Profile.objects.get)(user=owner)
    await terrain.share_dir_async(body, profile.cyverse_access_token, int(settings.HTTP_TIMEOUT))

    policies = await sync_to_async(DatasetAccessPolicy.objects.filter)(owner=request.user)
    datasets = []
    for policy in (await sync_to_async(list)(policies)):
        dataset = await sync_to_async(q.dataset_access_policy_to_dict)(policy)
        datasets.append(dataset)

    return JsonResponse({'datasets': datasets})


@sync_to_async
@login_required
@async_to_sync
async def unshare(request):
    """
    Revoke a user's access to a collection.

    Args:
        request: The request

    Returns:

    """

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
        guest = await sync_to_async(User.objects.get)(username=guest_username)
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

    await get_channel_layer().group_send(f"{guest.username}", {
        'type': 'push_notification',
        'notification': {
            'id': notification.guid,
            'username': notification.user.username,
            'created': notification.created.isoformat(),
            'message': notification.message,
            'read': notification.read,
        }
    })

    profile = await sync_to_async(Profile.objects.get)(user=owner)
    await terrain.unshare_dir_async(path, profile.cyverse_access_token, int(settings.HTTP_TIMEOUT))

    await sync_to_async(policy.delete)()
    policies = await sync_to_async(DatasetAccessPolicy.objects.filter)(owner=request.user)
    datasets = []
    for policy in (await sync_to_async(list)(policies)):
        dataset = await sync_to_async(q.dataset_access_policy_to_dict)(policy)
        datasets.append(dataset)

    return JsonResponse({'datasets': datasets})


@sync_to_async
@login_required
@async_to_sync
async def create(request):
    """
    Create a new collection.

    Args:
        request: The request

    Returns:

    """

    owner = request.user
    body = json.loads(request.body.decode('utf-8'))
    path = body['path']
    project = body.get('project', None)
    study = body.get('study', None)
    profile = await sync_to_async(Profile.objects.get)(user=owner)
    await terrain.create_dir_async(path, profile.cyverse_access_token, int(settings.HTTP_TIMEOUT))

    if project is not None and study is not None:
        try:
            investigation = await sync_to_async(Investigation.objects.get)(owner=owner, title=project['title'])
            study = await sync_to_async(Study.objects.get)(Investigation=investigation, title=study['title'])
        except:
            logger.warning(traceback.format_exc())
            return HttpResponseNotFound()

        if study.dataset_paths:
            study.dataset_paths.append(path)
        else:
            study.dataset_paths = [path]
        await sync_to_async(study.save)()
        logger.info(f"Bound {path} to project {project}, study {study}")
        return JsonResponse({'path': path, 'project': await sync_to_async(q.project_to_dict)(investigation)})
    else:
        return JsonResponse({'path': path})
