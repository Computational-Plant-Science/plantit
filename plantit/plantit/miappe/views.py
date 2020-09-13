import yaml
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response

from plantit.miappe.models import ObservedVariable, Sample, ObservationUnit, ExperimentalFactor, \
    EnvironmentParameter, BiologicalMaterial, Study, Investigation, Event, Role, File
from plantit.miappe.serializers import ObservedVariableSerializer, SampleSerializer, \
    ObservationUnitSerializer, EventSerializer, ExperimentalFactorSerializer, EnvironmentParameterSerializer, \
    BiologicalMaterialSerializer, FileSerializer, RoleSerializer, StudySerializer, InvestigationSerializer


class InvestigationViewSet(viewsets.ModelViewSet):
    queryset = Investigation.objects.all()
    serializer_class = InvestigationSerializer
    permission_classes = (IsAuthenticated,)


class StudyViewSet(viewsets.ModelViewSet):
    queryset = Study.objects.all()
    serializer_class = StudySerializer
    permission_classes = (IsAuthenticated,)


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = (IsAuthenticated,)


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = (IsAuthenticated,)


class BiologicalMaterialViewSet(viewsets.ModelViewSet):
    queryset = BiologicalMaterial.objects.all()
    serializer_class = BiologicalMaterialSerializer
    permission_classes = (IsAuthenticated,)


class EnvironmentParameterViewSet(viewsets.ModelViewSet):
    queryset = EnvironmentParameter.objects.all()
    serializer_class = EnvironmentParameterSerializer
    permission_classes = (IsAuthenticated,)

    with open("plantit/miappe/suggested_environment_parameters.yaml", 'r') as f:
        _suggested_environment_parameters = yaml.safe_load(f)

    @action(methods=['get'], detail=False)
    def suggested_environment_parameters(self, request):
        return Response({'suggested_environment_parameters': self._suggested_environment_parameters})


class ExperimentalFactorViewSet(viewsets.ModelViewSet):
    queryset = ExperimentalFactor.objects.all()
    serializer_class = ExperimentalFactorSerializer
    permission_classes = (IsAuthenticated,)

    with open("plantit/miappe/suggested_experimental_factors.yaml", 'r') as f:
        _suggested_experimental_factors = yaml.safe_load(f)

    @action(methods=['get'], detail=False)
    def suggested_experimental_factors(self, request):
        return Response({'suggested_experimental_factors': self._suggested_experimental_factors})


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (IsAuthenticated,)


class ObservationUnitViewSet(viewsets.ModelViewSet):
    queryset = ObservationUnit.objects.all()
    serializer_class = ObservationUnitSerializer
    permission_classes = (IsAuthenticated,)


class SampleViewSet(viewsets.ModelViewSet):
    queryset = Sample.objects.all()
    serializer_class = SampleSerializer
    permission_classes = (IsAuthenticated,)


class ObservedVariableViewSet(viewsets.ModelViewSet):
    queryset = ObservedVariable.objects.all()
    serializer_class = ObservedVariableSerializer
    permission_classes = (IsAuthenticated,)
