from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from plantit.targets.serializers import TargetSerializer
from plantit.targets.models import Target


class TargetsViewSet(viewsets.ModelViewSet):
    queryset = Target.objects.all()
    serializer_class = TargetSerializer
    permission_classes = (IsAuthenticated,)
