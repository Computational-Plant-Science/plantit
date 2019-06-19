import json
import posixpath
import importlib

from django.http import JsonResponse, Http404, HttpResponse
from django.contrib.auth.decorators import login_required

from plantit.workflows import registrar
from plantit.workflows import services
"""
    Defines a RESTFUL API for interacting with the file manager
"""

def workflows(request):
    """
        List the available workflows

        Args:
            request: the HTTP request
    """

    context = {
        "workflows": list(registrar.list.values())
    }

    return JsonResponse(context)

def parameters(request,workflow):

    params = importlib.import_module('workflows.' + workflow + '.workflow').parameters.copy()
    params.insert(0,services.default_params())

    return JsonResponse({"parameters": params})

def submit(request,workflow,pk):
    params = json.loads(request.body.decode('utf-8'))

    job_id = services.submit(request.user,workflow,pk,params)

    return JsonResponse({"job_id": job_id})
