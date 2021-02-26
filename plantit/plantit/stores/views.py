import asyncio
import json

import httpx
import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseNotFound, HttpResponseBadRequest, JsonResponse, HttpResponse
from rest_framework.decorators import api_view

from plantit.stores.models import DirectoryPolicy, DirectoryRole


def map_directory_policy(policy: DirectoryPolicy):
    return {
        'owner': policy.owner.username,
        'guest': policy.guest.username,
        'path': policy.path,
        'role': policy.role.value
    }


@login_required
def get_shared_directories(request):  # directories the current user has shared
    owner = request.user
    policies = DirectoryPolicy.objects.filter(owner=owner)
    return JsonResponse([map_directory_policy(policy) for policy in policies], safe=False)


@login_required
def get_directories_shared(request):  # directories shared with the current user
    guest = request.user
    policies = DirectoryPolicy.objects.filter(guest=guest)

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
def share_directory(request):
    owner = request.user
    guests = request.data['sharing']
    policies = []

    for guest in guests:
        try:
            user = User.objects.get(username=guest['user'])
        except:
            return HttpResponseNotFound()

        path = guest['paths'][0]['path']
        role = DirectoryRole.read if guest['paths'][0]['permission'].lower() == 'read' else DirectoryRole.write
        policy, created = DirectoryPolicy.objects.get_or_create(owner=owner, guest=user, role=role, path=path)
        policies.append({
            'created': created,
            'policy': map_directory_policy(policy)
        })

    response = requests.post("https://de.cyverse.org/terrain/secured/share",
                             data=json.dumps(request.data),
                             headers={"Authorization": f"Bearer {owner.profile.cyverse_token}", "Content-Type": 'application/json;charset=utf-8'})
    response.raise_for_status()
    return JsonResponse({'policies': policies})


@api_view(['POST'])
@login_required
def unshare_directory(request):
    owner = request.user
    guest_username = request.data['user']
    path = request.data['path']
    role_str = str(request.data['role'])

    if role_str.lower() != 'read' and role_str.lower() != 'write':
        return HttpResponseBadRequest(f"Unsupported role {role_str} (allowed: read, write)")
    else:
        role = DirectoryRole.read if role_str.lower() == 'read' else DirectoryRole.write

    try:
        guest = User.objects.get(username=guest_username)
    except:
        return HttpResponseNotFound()

    try:
        policy = DirectoryPolicy.objects.get(owner=owner, guest=guest, role=role, path=path)
    except:
        return HttpResponseNotFound()
    policy.delete()

    response = requests.post("https://de.cyverse.org/terrain/secured/unshare",
                             data=request.data,
                             headers={"Authorization": f"Bearer {owner.profile.cyverse_token}"})
    response.raise_for_status()
    return JsonResponse({'unshared': True})
