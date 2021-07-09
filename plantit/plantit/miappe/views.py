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
        projects = [project_to_dict(project) for project in
                    (Investigation.objects.all() if team is None else Investigation.objects.filter(team__username=team))]
        return JsonResponse({'projects': projects})
    elif request.method == 'POST':
        body = json.loads(request.body.decode('utf-8'))
        unique_id = f"plantit-projects-{request.user.username}-{body['title'].replace(' ', '-')}"

        if Investigation.objects.filter(unique_id=unique_id).count() > 0:
            return HttpResponseBadRequest('Duplicate title')

        project = Investigation.objects.create(
            owner=request.user,
            title=body['title'],
            unique_id=unique_id,
            description=body['description'] if 'description' in body else None)

        return JsonResponse(project_to_dict(project))


@login_required
def list_by_owner(request, owner):
    if request.method != 'GET': return HttpResponseNotAllowed()
    if request.user.username != owner: return HttpResponseForbidden()
    projects = [project_to_dict(project) for project in Investigation.objects.filter(owner=request.user)]
    return JsonResponse({'projects': projects})


@login_required
def get_or_delete(request, owner, title):
    if request.user.username != owner: return HttpResponseForbidden()

    if request.method == 'GET':
        try:
            project = Investigation.objects.get(owner=request.user, title=title)
            return JsonResponse(project_to_dict(project))
        except:
            return HttpResponseNotFound()
    elif request.method == 'DELETE':
        project = Investigation.objects.get(owner=request.user, title=title)
        project.delete()
        projects = [project_to_dict(project) for project in Investigation.objects.filter(owner=request.user)]
        return JsonResponse({'projects': projects})


@login_required
def exists(request, owner, title):
    if request.method != 'GET': return HttpResponseNotAllowed()
    if request.user.username != owner: return HttpResponseForbidden()

    try:
        Investigation.objects.get(owner=request.user, title=title)
        return JsonResponse({'exists': True})
    except:
        return JsonResponse({'exists': False})


@login_required
def add_team_member(request, owner, title):
    if request.method != 'POST': return HttpResponseNotAllowed()
    if request.user.username != owner: return HttpResponseForbidden()

    body = json.loads(request.body.decode('utf-8'))
    username = body['username']

    try:
        project = Investigation.objects.get(owner=request.user, title=title)
        user = User.objects.get(username=username)
    except:
        return HttpResponseNotFound()

    project.team.add(user)
    project.save()

    return JsonResponse(project_to_dict(project))


@login_required
def remove_team_member(request, owner, title):
    if request.method != 'POST': return HttpResponseNotAllowed()
    if request.user.username != owner: return HttpResponseForbidden()

    body = json.loads(request.body.decode('utf-8'))
    username = body['username']

    try:
        project = Investigation.objects.get(owner=request.user, title=title)
        user = User.objects.get(username=username)
    except:
        return HttpResponseNotFound()

    project.team.remove(user)
    project.save()

    return JsonResponse(project_to_dict(project))


@login_required
def add_study(request, owner, title):
    if request.method != 'POST': return HttpResponseNotAllowed()
    if request.user.username != owner: return HttpResponseForbidden()

    body = json.loads(request.body.decode('utf-8'))
    study_title = body['title']
    study_description = body['description']

    try:
        project = Investigation.objects.get(owner=request.user, title=title)
    except:
        return HttpResponseNotFound()

    study = Study.objects.create(investigation=project, title=study_title, description=study_description)
    return JsonResponse(project_to_dict(project))


@login_required
def remove_study(request, owner, title):
    if request.method != 'POST': return HttpResponseNotAllowed()
    if request.user.username != owner: return HttpResponseForbidden()

    body = json.loads(request.body.decode('utf-8'))
    study_title = body['title']

    try:
        project = Investigation.objects.get(owner=request.user, title=title)
        study = Study.objects.get(investigation=project, title=study_title)
    except:
        return HttpResponseNotFound()

    study.delete()
    return JsonResponse(project_to_dict(project))
