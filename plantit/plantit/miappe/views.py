import json
import uuid

import yaml
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseNotFound, HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response

from plantit.miappe.models import ObservedVariable, Sample, ObservationUnit, ExperimentalFactor, \
    EnvironmentParameter, BiologicalMaterial, Study, Investigation, Event, DataFile
from plantit.utils import project_to_dict


@login_required
def suggested_environment_parameters(request):
    with open("plantit/miappe/suggested_environment_parameters.yaml", 'r') as file:
        return JsonResponse({'suggested_environment_parameters': yaml.safe_load(file)})


@login_required
def suggested_experimental_factors(request):
    with open("plantit/miappe/suggested_experimental_factors.yaml", 'r') as file:
        return JsonResponse({'suggested_experimental_factors': yaml.safe_load(file)})


@login_required
def list_or_create(request):
    if request.method == 'GET':
        team = request.GET.get('team', None)
        projects = [project_to_dict(investigation) for investigation in
                    (Investigation.objects.all() if team is None else Investigation.objects.filter(team__username=team))]
        return JsonResponse({'projects': projects})
    elif request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))
        unique_id = f"plantit-projects-{request.user.username}-{body['title']}"

        if Investigation.objects.filter(unique_id=unique_id).count() > 0:
            return HttpResponseBadRequest('Duplicate title')

        investigation = Investigation.objects.create(
            owner=request.user,
            title=body['title'],
            unique_id=f"plantit-projects-{request.user.username}-{body['title']}",
            description=body['description'] if 'description' in body else None)

        return JsonResponse(project_to_dict(investigation))


@login_required
def list_by_owner(request, owner):
    if request.method != 'GET': return HttpResponseNotAllowed()
    if request.user.username != owner: return HttpResponseForbidden()
    projects = [project_to_dict(project) for project in Investigation.objects.filter(owner=request.user)]
    return JsonResponse({'projects': projects})


@login_required
def get_by_owner_and_unique_id(request, owner, id):
    if request.method != 'GET': return HttpResponseNotAllowed()
    if request.user.username != owner: return HttpResponseForbidden()

    try:
        investigation = Investigation.objects.get(owner=request.user, unique_id=id)
        return JsonResponse(project_to_dict(investigation))
    except:
        return HttpResponseNotFound()


@login_required
def exists(request, owner, id):
    if request.method != 'GET': return HttpResponseNotAllowed()
    if request.user.username != owner: return HttpResponseForbidden()

    try:
        investigation = Investigation.objects.get(owner=request.user, unique_id=id)
        return JsonResponse({'exists': True})
    except:
        return JsonResponse({'exists': False})


@login_required
def delete(request, owner, id):
    if request.method != 'DELETE': return HttpResponseNotAllowed()
    if request.user.username != owner: return HttpResponseForbidden()

    try:
        investigation = Investigation.objects.get(owner=request.user, unique_id=id)
        investigation.delete()
        return HttpResponse()
    except:
        return HttpResponseNotFound()


@login_required
def add_team_member(request, owner, id):
    if request.method != 'POST': return HttpResponseNotAllowed()
    if request.user.username != owner: return HttpResponseForbidden()

    body = json.loads(request.body.decode('utf-8'))
    username = body['username']

    try:
        investigation = Investigation.objects.get(owner=request.user, unique_id=id)
        user = User.objects.get(username=username)
    except:
        return HttpResponseNotFound()

    investigation.team.add(user)
    investigation.save()

    return JsonResponse(project_to_dict(investigation))


@login_required
def remove_team_member(request, owner, id):
    if request.method != 'POST': return HttpResponseNotAllowed()
    if request.user.username != owner: return HttpResponseForbidden()

    body = json.loads(request.body.decode('utf-8'))
    username = body['username']

    try:
        investigation = Investigation.objects.get(owner=request.user, unique_id=id)
        user = User.objects.get(username=username)
    except:
        return HttpResponseNotFound()

    investigation.team.remove(user)
    investigation.save()

    return JsonResponse(project_to_dict(investigation))
