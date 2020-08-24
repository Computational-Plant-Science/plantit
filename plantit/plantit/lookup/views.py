import yaml
from django.http import HttpResponseNotFound
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class LookupViewSet(viewsets.ViewSet):

    with open("plantit/lookups/countries.yaml", 'r') as f:
        _countries = yaml.safe_load(f)

    with open("plantit/lookups/universities.yaml", 'r') as f:
        _universities = yaml.safe_load(f)

    with open("plantit/lookups/miappe_environment_parameters.yaml", 'r') as f:
        _miappe_environment_parameters = yaml.safe_load(f)

    with open("plantit/lookups/miappe_experimental_factors.yaml", 'r') as f:
        _miappie_experimental_factors = yaml.safe_load(f)

    @action(methods=['get'], detail=False)
    def countries(self, request):
        return Response({'countries': self._countries})

    @action(methods=['get'], detail=False)
    def universities(self, request):
        country = request.GET.get('country', None)
        if country in self._universities:
            return Response({'universities': self._universities[country]})
        else:
            return HttpResponseNotFound()

    @action(methods=['get'], detail=False)
    def miappe_environment_parameters(self, request):
        return Response({'miappe_environment_parameters': self._miappe_environment_parameters})

    @action(methods=['get'], detail=False)
    def miappe_experimental_factors(self, request):
        return Response({'miappe_experimental_factors': self._miappie_experimental_factors})