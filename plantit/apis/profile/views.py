from rest_framework import viewsets
from django.contrib.auth.models import User

from apis.profile.serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated

class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint returning user info.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)


