from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import action

from plantit.runs.models.run import Run
from .serializers import JobSerializer
from rest_framework.permissions import IsAuthenticated
from ..mixins import PinViewMixin
from django.contrib.auth.decorators import login_required
from plantit.stores.services import download_stream


class RunViewSet(viewsets.ModelViewSet, PinViewMixin):
    permission_classes = (IsAuthenticated,)

    queryset = Run.objects.all()
    serializer_class = JobSerializer

    def get_queryset(self):
        if not self.request.user.is_anonymous:
            user = self.request.user
            return self.queryset.filter(user=user)
        else:
            # If no user info, return all jobs.
            # This will happen if access the jobs via a token.
            # TODO: restrict to job with given token.
            return self.queryset


@action(methods=['get'], detail=False)
@login_required
def get_run(request):
    run = Run.objects.get(user=request.user, submission_id=request.GET.get('id', None))
    return JsonResponse(run)


@login_required
def download_results(request, pk):
    """
        Stream the results file from a job to the the user.

        **url:** `/apis/v1/jobs/<job_pk>/download_results/`

        **Response Data:** A HTTP streaming response.

        **Requires:** User must be logged in.
    """
    run = Run.objects.get(pk=pk)

    return download_stream(run.collection.storage_type,
                           run.remote_results_path,
                           request.user)
