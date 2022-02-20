import json
import uuid
import logging

import yaml
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseNotFound
from django.utils.dateparse import parse_date
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

import plantit.queries as q
from plantit.miappe.models import EnvironmentParameter, ExperimentalFactor, Study, Investigation

logger = logging.getLogger(__name__)


# @swagger_auto_schema(methods='get')
@login_required
@api_view(['GET'])
def suggested_environment_parameters(request):
    with open("plantit/miappe/suggested_environment_parameters.yaml", 'r') as file:
        return JsonResponse({'suggested_environment_parameters': yaml.safe_load(file)})


# @swagger_auto_schema(methods='get')
@login_required
@api_view(['GET'])
def suggested_experimental_factors(request):
    with open("plantit/miappe/suggested_experimental_factors.yaml", 'r') as file:
        return JsonResponse({'suggested_experimental_factors': yaml.safe_load(file)})


# @swagger_auto_schema(method='post', auto_schema=None)
@swagger_auto_schema(methods='get')
@login_required
@api_view(['GET', 'POST'])
def list_or_create(request):
    if request.method == 'GET':
        team = request.GET.get('team', None)
        projects = [q.project_to_dict(project) for project in
                    (Investigation.objects.all() if team is None else Investigation.objects.filter(team__username=team))]
        return JsonResponse({'projects': projects})
    elif request.method == 'POST':
        body = request.data
        title = body['title']
        description = body['description'] if 'description' in body else None
        if Investigation.objects.filter(title=title).count() > 0: return HttpResponseBadRequest('Duplicate title')
        project = Investigation.objects.create(owner=request.user, guid=str(uuid.uuid4()), title=title, description=description)
        return JsonResponse(q.project_to_dict(project))


# @swagger_auto_schema(methods='get')
@login_required
@api_view(['GET'])
def list_by_owner(request, owner):
    if request.method != 'GET': return HttpResponseNotAllowed()
    if request.user.username != owner: return HttpResponseForbidden()
    projects = [q.project_to_dict(project) for project in Investigation.objects.filter(owner=request.user)]
    return JsonResponse({'projects': projects})


# @swagger_auto_schema(method='delete', auto_schema=None)
# @swagger_auto_schema(methods='get')
@login_required
@api_view(['GET', 'DELETE'])
def get_or_delete(request, owner, title):
    if request.user.username != owner: return HttpResponseForbidden()
    if request.method == 'GET':
        try:
            project = Investigation.objects.get(owner=request.user, title=title)
            return JsonResponse(q.project_to_dict(project))
        except:
            return HttpResponseNotFound()
    elif request.method == 'DELETE':
        project = Investigation.objects.get(owner=request.user, title=title)
        project.delete()
        projects = [q.project_to_dict(project) for project in Investigation.objects.filter(owner=request.user)]
        return JsonResponse({'projects': projects})


# @swagger_auto_schema(methods='get')
@login_required
@api_view(['GET'])
def exists(request, owner, title):
    if request.method != 'GET': return HttpResponseNotAllowed()
    if request.user.username != owner: return HttpResponseForbidden()
    try:
        Investigation.objects.get(owner=request.user, title=title)
        return JsonResponse({'exists': True})
    except:
        return JsonResponse({'exists': False})


# @swagger_auto_schema(methods='post')
@login_required
@api_view(['POST'])
def add_team_member(request, owner, title):
    if request.method != 'POST': return HttpResponseNotAllowed()
    if request.user.username != owner: return HttpResponseForbidden()

    body = request.data
    username = body['username']

    try:
        project = Investigation.objects.get(owner=request.user, title=title)
        user = User.objects.get(username=username)
    except:
        return HttpResponseNotFound()

    project.team.add(user)
    project.save()

    return JsonResponse(q.project_to_dict(project))


# @swagger_auto_schema(methods='post')
@login_required
@api_view(['POST'])
def remove_team_member(request, owner, title):
    if request.method != 'POST': return HttpResponseNotAllowed()
    if request.user.username != owner: return HttpResponseForbidden()

    body = request.data
    username = body['username']

    try:
        project = Investigation.objects.get(owner=request.user, title=title)
        user = User.objects.get(username=username)
    except:
        return HttpResponseNotFound()

    project.team.remove(user)
    project.save()

    return JsonResponse(q.project_to_dict(project))


# @swagger_auto_schema(methods='post')
@login_required
@api_view(['POST'])
def add_study(request, owner, title):
    if request.method != 'POST': return HttpResponseNotAllowed()
    if request.user.username != owner: return HttpResponseForbidden()

    body = request.data
    study_title = body['title']
    study_description = body['description']
    guid = f"{request.user.username}-{title.replace(' ', '-')}-{study_title.replace(' ', '-')}"

    try:
        project = Investigation.objects.get(owner=request.user, title=title)
    except:
        return HttpResponseNotFound()

    study = Study.objects.create(investigation=project, title=study_title, guid=guid, description=study_description)
    return JsonResponse(q.project_to_dict(project))


# @swagger_auto_schema(methods='post')
@login_required
@api_view(['POST'])
def remove_study(request, owner, title):
    if request.method != 'POST': return HttpResponseNotAllowed()
    if request.user.username != owner:
        print(request.user.username)
        print(owner)
        return HttpResponseForbidden()

    body = request.data
    study_title = body['title']

    try:
        project = Investigation.objects.get(owner=request.user, title=title)
        study = Study.objects.get(investigation=project, title=study_title)
    except:
        return HttpResponseNotFound()

    study.delete()
    return JsonResponse(q.project_to_dict(project))


# @swagger_auto_schema(methods='post')
@login_required
@api_view(['POST'])
def edit_study(request, owner, title):
    if request.method != 'POST': return HttpResponseNotAllowed()
    if request.user.username != owner: return HttpResponseForbidden()

    body = request.data
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
    study_environment_parameters = body['environment_parameters'] if 'environment_parameters' in body else None
    study_experimental_factors = body['experimental_factors'] if 'experimental_factors' in body else None

    try:
        project = Investigation.objects.get(owner=request.user, title=title)
        study = Study.objects.get(investigation=project, title=study_title)
        environment_parameters = list(EnvironmentParameter.objects.filter(study=study))
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

    for existing in environment_parameters:
        existing.delete()

    for name, value in study_environment_parameters.items():
        EnvironmentParameter.objects.create(name=name, value=value, study=study)

    return JsonResponse(q.project_to_dict(project))
