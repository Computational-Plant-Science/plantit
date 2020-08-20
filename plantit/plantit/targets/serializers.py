from rest_framework import serializers

from plantit.targets.target import Target


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ('name', 'description', 'hostname', 'pre_commands')