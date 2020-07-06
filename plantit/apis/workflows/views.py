import json

import requests
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse

from apis.util import get_config
from plantit.workflows import services


@login_required
def workflows(request):
    token = request.user.profile.github_auth_token
    items = requests.get(
        f"https://api.github.com/search/code?q=filename:plantit.yaml+org:computational-plant-science",
        headers={"Authorization": f"token {token}"}
    ).json()['items']
    return JsonResponse({
        'workflows': [{
            'repo': item['repository'],
            'config': get_config(item['repository'], token)
        } for item in items]
    })


@login_required
def workflow(request, owner, name):
    token = request.user.profile.github_auth_token
    repo = requests.get(f"https://api.github.com/repos/{owner}/{name}",
                        headers={"Authorization": f"token {token}"}).json()
    config = get_config(repo, token)
    return JsonResponse({
        'repo': repo,
        'config': config
    })


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
