from rest_framework import viewsets
from .serializers import JobSerializer
from plantit.job_manager.job import Job, Task
from plantit.job_manager.authentication import JobTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from ..mixins import PinViewMixin

class JobViewSet(viewsets.ModelViewSet, PinViewMixin):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = (IsAuthenticated,)

    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def get_queryset(self):
        if(not self.request.user.is_anonymous):
            user = self.request.user
            return self.queryset.filter(user=user)
        else:
            # If no user info, return all jobs.
            # This will happen if access the jobs via a token.
            # TODO: restrict to job with given token.
            return self.queryset
