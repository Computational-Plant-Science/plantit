from rest_framework import serializers
from django.contrib.auth.models import User

from plantit.user.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('country', 'continent', 'affiliated_institution', 'affiliated_institution_type', 'field_of_study')


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'last_login', 'date_joined', 'profile')
