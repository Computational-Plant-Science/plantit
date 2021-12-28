import json
import uuid

import yaml
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseNotFound, HttpResponse
from django.utils.dateparse import parse_date
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response

from plantit.miappe.models import ObservedVariable, Sample, ObservationUnit, BiologicalMaterial, Study, Investigation, Event, DataFile
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
    unique_id = f"plantit-projects-{request.user.username}-{title.replace(' ', '-')}-{study_title.replace(' ', '-')}"

    try:
        project = Investigation.objects.get(owner=request.user, title=title)
    except:
        return HttpResponseNotFound()

    study = Study.objects.create(investigation=project, title=study_title, unique_id=unique_id, description=study_description)
    return JsonResponse(project_to_dict(project))


@login_required
def remove_study(request, owner, title):
    if request.method != 'POST': return HttpResponseNotAllowed()
    if request.user.username != owner:
        print(request.user.username)
        print(owner)
        return HttpResponseForbidden()

    body = json.loads(request.body.decode('utf-8'))
    study_title = body['title']

    try:
        project = Investigation.objects.get(owner=request.user, title=title)
        study = Study.objects.get(investigation=project, title=study_title)
    except:
        return HttpResponseNotFound()

    study.delete()
    return JsonResponse(project_to_dict(project))


@login_required
def edit_study(request, owner, title):
    if request.method != 'POST': return HttpResponseNotAllowed()
    if request.user.username != owner: return HttpResponseForbidden()

    body = json.loads(request.body.decode('utf-8'))
    study_title = body['title']
    study_start_date = parse_date(body['start_date'])
    study_end_date = parse_date(body['end_date']) if 'end_date' in body and body['end_date'] is not None else None
    study_contact_institution = body['contact_institution'] if 'contact_institution' in body else None
    study_country = body['country'] if 'country' in body else None
    study_site_name = body['site_name'] if 'site_name' in body else None
    study_latitude = float(body['latitude']) if 'latitude' in body and body['latitude'] is not None else None
    study_longitude = float(body['longitude']) if 'longitude' in body and body['longitude'] is not None else None
    study_altitude = int(body['altitude']) if 'altitude' in body and body['altitude'] is not None else None
    study_altitude_units = body['altitude_units'] if 'altitude_units' in body else None
    study_experimental_design_description = body['experimental_design_description'] if 'experimental_design_description' in body else None
    study_experimental_design_type = body['experimental_design_type'] if 'experimental_design_type' in body else None
    study_observation_unit_description = body['observation_unit_description'] if 'observation_unit_description' in body else None
    study_growth_facility_description = body['growth_facility_description'] if 'growth_facility_description' in body else None
    study_growth_facility_type = body['growth_facility_type'] if 'growth_facility_type' in body else None
    study_cultural_practices = body['cultural_practices'] if 'cultural_practices' in body else None

    try:
        project = Investigation.objects.get(owner=request.user, title=title)
        study = Study.objects.get(investigation=project, title=study_title)
    except:
        return HttpResponseNotFound()

    study.description = body['description']
    study.start_date = study_start_date
    study.end_date = study_end_date
    study.contact_institution = study_contact_institution
    study.country = study_country
    study.site_name = study_site_name
    study.latitude = study_latitude
    study.longitude = study_longitude
    study.altitude = study_altitude
    study.altitude_units = study_altitude_units
    study.experimental_design_description = study_experimental_design_description
    study.experimental_design_type = study_experimental_design_type
    # study.experimental_design_map = body['experimental_design_map']
    # study.observation_unit_level_hierarchy = body['observation_unit_level_hierarchy']
    study.observation_unit_description = study_observation_unit_description
    study.growth_facility_description = study_growth_facility_description
    study.growth_facility_type = study_growth_facility_type
    study.cultural_practices = study_cultural_practices
    study.save()

    return JsonResponse(project_to_dict(project))
