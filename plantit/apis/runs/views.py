from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotFound, HttpResponse
from rest_framework.decorators import action, api_view

from plantit.runs.models.run import Run
from plantit.runs.models.status import Status


@action(methods=['get'], detail=False)
@login_required
def get_runs(request):
    runs = Run.objects.all()

    return JsonResponse([{
        'id': run.identifier,
        'work_dir': run.work_dir,
        'cluster': run.cluster.name,
        'created': run.created,
        'state': run.status.state if run.status is not None else 'Unknown',
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
        'state': run.status.state if run.status is not None else 'Unknown',
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

    return JsonResponse([
        {
            'run_id': id,
            'state': status.state,
            'location': status.location,
            'date': status.date,
            'description': status.description
        } for status in list(run.status_set.all())], safe=False)


@api_view(['POST'])
@login_required
def update_status(request, id):
    status = request.data
    state = int(status['state'])

    if state == 2:
        state = Status.FAILED
    elif state == 3:
        state = Status.RUNNING
    elif state == 4:
        state = Status.CREATED
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
            run.status_set.create(description=line, state=state, location=run.cluster.name)

    run.save()

    return HttpResponse(status=200)


@login_required
def get_results(request, pk):
    pass
    # run = Run.objects.get(pk=pk)
    # return download_stream(request, run.remote_results_path)

