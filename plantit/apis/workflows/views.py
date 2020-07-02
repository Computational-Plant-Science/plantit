import importlib
import json

import requests
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework.response import Response

from plantit.workflows import registrar
from plantit.workflows import services


@login_required
def workflows(request):
    response = requests.get(f"https://api.github.com/search/code?q=filename:plantit.yaml+org:computational-plant-science")
    hits = response.json()['items']
    repos = [hit['repository'] for hit in hits]
    return Response(repos)


# @login_required
# def workflows(request):
#     """
#         Lists the available workflows.
#
#         **url:** `/apis/v1/workflows/`
#
#         **Response Data:**  A JSON object with the "workflows" attribute.
#             The workflow attribute contains a JSON array with
#             1 object per workflow.
#
#         **Requires:** User must be logged in.
#
#         Example:
#             .. code-block:: javascript
#
#                 {"workflows": [
#                     {
#                         "name": "Test Workflow",
#                         "description": "asfd",
#                         "icon_loc": "workflows/test_workflow/icon.png",
#                         "api_version": 0.1,
#                         "app_name": "test_workflow",
#                         "singularity_url": "shub://frederic-michaud/python3",
#                         "app_url_pattern": "workflows:test_workflow:analyze"
#                      }
#                   ]
#                 }
#     """
#
#     context = {
#         "workflows": list(registrar.list.values())
#     }
#
#     return JsonResponse(context)

@login_required
def workflow(request, workflow):
    """
        **url:** `/apis/v1/workflows/<workflow app_name>/`

        **Requires:** User must be logged in.

        Example:
            .. code-block:: javascript

                {
                    "parameters":{
                        'id': 'settings',
                        'name': 'Workflow Settings',
                        'params':[
                            {
                                'id': 'example1',
                                'type': 'bool',
                                'initial': False,
                                'name': 'Example Checkbox',
                                'description': 'Example of a true/false workflow parameter'
                            },
                            {
                                'id': 'example2',
                                'type': 'float',
                                'initial': 1.0,
                                'name': 'Example Float Value',
                                'description': 'Example of a float workflow parameter'
                            }
                        ]
                    }
                }

    """
    params = importlib.import_module('workflows.' + workflow + '.workflow').parameters.copy()
    params.insert(0, services.default_params())

    context = {
        "workflow": registrar.list[workflow],
        "parameters": params
    }

    return JsonResponse(context)

@login_required
def submit(request, workflow, pk):
    """
        Submit a collection for analysis by a workflow.

        **url:** `/apis/v1/workflows/<workflow app_name>/`

        **Body Data:**
            JSON object containing the user's choices for
            workflow parameters. JSON object should be in the
            format accepted by the Plant IT cookiecutter process function.
            (i.e. params are passed into process as the args variable).

        **Response Data:**  A JSON object containing the "job_id"

        **Requires:** User must be logged in.

        Example:
            .. code-block:: javascript

                {"job_id": 12}
    """
    params = json.loads(request.body.decode('utf-8'))

    job_id = services.submit(request.user, workflow, pk, params)

    return JsonResponse({"job_id": job_id})
