from rest_framework import viewsets, mixins
from django.contrib.auth.models import User

from apis.profile.serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated


class ProfileViewSet(viewsets.ModelViewSet, mixins.RetrieveModelMixin):
    """
    API endpoint returning user info.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
