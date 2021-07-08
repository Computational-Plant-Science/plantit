import json

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


@login_required
def suggested_environment_parameters(request):
    with open("plantit/miappe/suggested_environment_parameters.yaml", 'r') as file:
        return JsonResponse({'suggested_environment_parameters': yaml.safe_load(file)})


@login_required
def suggested_experimental_factors(request):
    with open("plantit/miappe/suggested_experimental_factors.yaml", 'r') as file:
        return JsonResponse({'suggested_experimental_factors': yaml.safe_load(file)})


def person_to_dict(user: User, role: str) -> dict:
    return {
        'name': f"{user.first_name} {user.last_name}",
        'email': user.email,
        'id': user.username,
        'affiliation': user.profile.institution,
        'role': role,
    }


def study_to_dict(study: Study) -> dict:
    team = [person_to_dict(person, 'Researcher') for person in study.team.all()]
    return {
        'unique_id': study.unique_id,
        'title': study.title,
        'description': study.description,
        'start_date': study.start_date,
        'end_date': study.end_date,
        'contact_institution': study.contact_institution,
        'country': study.country,
        'site_name': study.site_name if study.site_name != '' else None,
        'latitude': study.latitude,
        'longitude': study.longitude,
        'altitude': study.altitude,
        'experimental_design_description': study.experimental_design_description if study.experimental_design_description != '' else None,
        'experimental_design_type': study.experimental_design_type if study.experimental_design_type != '' else None,
        'experimental_design_map': study.experimental_design_map if study.experimental_design_map != '' else None,
        'observation_unit_level_hierarchy': study.observation_unit_level_hierarchy if study.observation_unit_level_hierarchy != '' else None,
        'observation_unit_description': study.observation_unit_description if study.observation_unit_description != '' else None,
        'growth_facility_description': study.growth_facility_description if study.growth_facility_description != '' else None,
        'growth_facility_type': study.growth_facility_type if study.growth_facility_type != '' else None,
        'cultural_practices': study.cultural_practices if study.cultural_practices != '' else None,
        'team': team,
    }


def investigation_to_dict(investigation: Investigation) -> dict:
    studies = [study_to_dict(study) for study in Study.objects.filter(investigation=investigation)]
    team = [person_to_dict(person, 'Researcher') for person in investigation.team.all()]
    return {
        'unique_id': investigation.unique_id,
        'owner': investigation.owner.username,
        'title': investigation.title,
        'description': investigation.description,
        'submission_date': investigation.submission_date,
        'public_release_date': investigation.public_release_date,
        'associated_publication': investigation.associated_publication,
        'studies': studies,
        'team': team
    }


@login_required
def list_all_investigations(request):
    if request.method != 'GET': return HttpResponseNotAllowed()
    team = request.GET.get('team', None)
    investigations = [investigation_to_dict(investigation) for investigation in
                      (Investigation.objects.all() if team is None else Investigation.objects.filter(team__username=team))]
    return JsonResponse({'investigations': investigations})


@login_required
def list_investigations_by_owner(request, owner):
    if request.method != 'GET': return HttpResponseNotAllowed()
    if request.user.username != owner: return HttpResponseForbidden()
    investigations = [investigation_to_dict(investigation) for investigation in Investigation.objects.filter(owner=request.user)]
    return JsonResponse({'investigations': investigations})


@login_required
def get_investigation(request, owner, id):
    if request.method != 'GET': return HttpResponseNotAllowed()
    if request.user.username != owner: return HttpResponseForbidden()

    try:
        investigation = Investigation.objects.get(owner=request.user, unique_id=id)
        return JsonResponse(investigation_to_dict(investigation))
    except:
        return HttpResponseNotFound()


@login_required
def investigation_exists(request, owner, id):
    if request.method != 'GET': return HttpResponseNotAllowed()
    if request.user.username != owner: return HttpResponseForbidden()

    try:
        investigation = Investigation.objects.get(owner=request.user, unique_id=id)
        return JsonResponse({'exists': True})
    except:
        return JsonResponse({'exists': False})


@login_required
def delete_investigation(request, owner, id):
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
    print(username)

    try:
        investigation = Investigation.objects.get(owner=request.user, unique_id=id)
        user = User.objects.get(username=username)
    except:
        return HttpResponseNotFound()

    investigation.team.add(user)
    investigation.save()

    return JsonResponse(investigation_to_dict(investigation))


@login_required
def remove_team_member(request, owner, id):
    if request.method != 'POST': return HttpResponseNotAllowed()
    if request.user.username != owner: return HttpResponseForbidden()

    body = json.loads(request.body.decode('utf-8'))
    username = body['username']
    print(username)

    try:
        investigation = Investigation.objects.get(owner=request.user, unique_id=id)
        user = User.objects.get(username=username)
    except:
        return HttpResponseNotFound()

    investigation.team.remove(user)
    investigation.save()

    return JsonResponse(investigation_to_dict(investigation))
