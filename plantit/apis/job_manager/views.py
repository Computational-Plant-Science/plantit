from rest_framework import viewsets
from .serializers import JobSerializer
from plantit.job_manager.job import Job
from rest_framework.permissions import IsAuthenticated
from ..mixins import PinViewMixin
from django.contrib.auth.decorators import login_required
from plantit.file_manager.services import download_stream


class JobViewSet(viewsets.ModelViewSet, PinViewMixin):
    """
        List a user's jobs and job information.

        **url:** `/apis/v1/jobs`

        **Response Data:** A json array with 1 object per job.

        **Requires:** User must be logged in.

        Extends PineViewMixin, which provides the following extra urls:

        - `/apis/v1/jobs/<pk>/pin`: Pin the job with the given pk to the user
        - `/apis/v1/jobs/<pk>/unpin`: Unpin the job with the given pk to the user

        Example:
            .. code-block:: javascript

                [
                    {
                        "pk": 10,
                        "pinned": false,
                        "collection": "Test",
                        "date_created": "2019-06-19T15:09:26.609002-04:00",
                        "work_dir": "1560989366/",
                        "workflow": "test_workflow",
                        "submission_id": null,
                        "cluster": "Sapelo2",
                        "remote_results_path": "/tempZone/home/rods/results_job10.csv",
                        "task_set": [
                            {
                                "pk": 19,
                                "complete": true
                            },
                            {
                                "pk": 20,
                                "complete": true
                            }
                        ],
                        "status_set": [
                            {
                                "state": 1,
                                "date": "2019-06-19T15:10:18.394814-04:00",
                                "description": "All Tasks Finished"
                            },
                            {
                                "state": 3,
                                "date": "2019-06-19T15:09:31.024499-04:00",
                                "description": "Running"
                            },
                            {
                                "state": 3,
                                "date": "2019-06-19T15:09:27.888250-04:00",
                                "description": "Queued"
                            },
                            {
                                "state": 3,
                                "date": "2019-06-19T15:09:26.662478-04:00",
                                "description": "Submitted"
                            },
                            {
                                "state": 5,
                                "date": "2019-06-19T15:09:26.625078-04:00",
                                "description": "Created"
                            }
                        ]
                    },
                ]
    """
    permission_classes = (IsAuthenticated,)

    queryset = Job.objects.all()
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


@login_required
def download_results(request, pk):
    """
        Stream the results file from a job to the the user.

        **url:** `/apis/v1/jobs/<job_pk>/download_results/`

        **Response Data:** A HTTP streaming response.

        **Requires:** User must be logged in.
    """
    job = Job.objects.get(pk=pk)

    return download_stream(job.collection.storage_type,
                           job.remote_results_path,
                           request.user)
