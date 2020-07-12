from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action, api_view

from plantit.runs.models.run import Run
from plantit.runs.models.status import TargetStatus
from plantit.stores.services import download_stream


@action(methods=['get'], detail=False)
@login_required
def get_runs(request):
    runs = Run.objects.all()

    return JsonResponse([{
        'id': run.identifier,
        'work_dir': run.work_dir,
        'cluster': run.cluster.name,
        'created': run.created,
        'state': run.plantit_status.state if run.plantit_status is not None else 'Unknown',
        'workflow_owner': run.workflow_owner,
        'workflow_name': run.workflow_name
    } for run in runs], safe=False)


@action(methods=['get'], detail=False)
@login_required
def get_run(request, id):
    try:
        run = Run.objects.get(identifier=id)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    return JsonResponse({
        'id': run.identifier,
        'work_dir': run.work_dir,
        'cluster': run.cluster.name,
        'created': run.created,
        'state': run.plantit_status.state if run.plantit_status is not None else 'Unknown',
        'workflow_owner': run.workflow_owner,
        'workflow_name': run.workflow_name
    })


@action(methods=['get'], detail=False)
@login_required
def get_status(request, id):
    try:
        run = Run.objects.get(identifier=id)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    return JsonResponse({
        'plantit': [{
            'run_id': id,
            'state': status.state,
            'date': status.date,
            'description': status.description
        } for status in list(run.plantitstatus_set.all())],
        'target': [{
            'run_id': id,
            'state': status.state,
            'date': status.date,
            'description': status.description
        } for status in list(run.targetstatus_set.all())],
    })


@api_view(['POST'])
@login_required
def update_target_status(request, id):
    status = request.data
    state = int(status['state'])

    if state == 2:
        state = TargetStatus.FAILED
    elif state == 3:
        state = TargetStatus.RUNNING
    elif state == 4:
        state = TargetStatus.CREATED
    else:
        raise ValueError(f"Invalid value for state '{status['state']}' (expected 2 - 4)")

    try:
        run = Run.objects.get(identifier=id)
    except Run.DoesNotExist:
        return HttpResponseNotFound()

    for chunk in status['description'].split('<br>'):
        for line in chunk.split('\n'):
            if 'old time stamp' in line or 'image path' in line or 'Cache folder' in line or line == '':
                continue
            run.targetstatus_set.create(description=line, state=state)

    run.save()

    return HttpResponse(status=200)


@login_required
def get_results(request, pk):
    run = Run.objects.get(pk=pk)

    return download_stream(run.collection.storage_type,
                           run.remote_results_path,
                           request.user)
