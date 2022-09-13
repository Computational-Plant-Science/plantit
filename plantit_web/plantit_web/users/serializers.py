from rest_framework import serializers
from django.contrib.auth.models import User

from plantit_web.users.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('github_username',
                  'github_token',
                  'cyverse_access_token',
                  'dark_mode',
                  'push_notification_sub_arn',
                  'institution',
                  'first_login')


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    def create(self, validated_data):
        data = validated_data.get('profile')
        user = User.objects.create(**validated_data)
        Profile.objects.create(user=user, **data)
        return user

    def update(self, instance, validated_data):
        if validated_data.get('first_name'):
            instance.first_name = validated_data.get('first_name')

        if validated_data.get('last_name'):
            instance.last_name = validated_data.get('last_name')

        if validated_data.get('profile'):
            serializer = ProfileSerializer(data=validated_data.get('profile'))
            if serializer.is_valid():
                profile = serializer.update(instance=instance.profile, validated_data=validated_data.get('profile'))
                instance.profile = profile

        instance.save()

        return instance

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'last_login', 'date_joined', 'profile')