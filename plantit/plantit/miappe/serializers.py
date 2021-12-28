from rest_framework import serializers

from plantit.miappe.models import *


class InvestigationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investigation
        fields = '__all__'


class StudySerializer(serializers.ModelSerializer):
    class Meta:
        model = Study
        fields = '__all__'


class DataFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataFile
        fields = '__all__'


class BiologicalMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiologicalMaterial
        fields = '__all__'


class EnvironmentParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvironmentParameter
        fields = '__all__'


class ExperimentalFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperimentalFactor
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class ObservationUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObservationUnit
        fields = '__all__'


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = '__all__'


class ObservedVariableSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObservedVariable
        fields = '__all__'
