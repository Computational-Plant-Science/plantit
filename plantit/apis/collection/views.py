from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404, HttpResponseNotFound
from rest_framework import viewsets

from plantit.stores.irodsstore import IRODS, IRODSOptions
from .serializers import CollectionSerializer, SampleSerializer
from plantit.collection.models import Collection, Sample
from rest_framework.permissions import IsAuthenticated
from ..mixins import PinViewMixin


class CollectionViewSet(viewsets.ModelViewSet, PinViewMixin):
    """
    API endpoint that allows collections to be viewed and edited.
    """
    permission_classes = (IsAuthenticated,)

    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(user=user)


class SampleViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows collections to be viewed and edited.
    """
    permission_classes = (IsAuthenticated,)

    queryset = Sample.objects.all()
    serializer_class = SampleSerializer
    #
    # def get_queryset(self):
    #     user = self.request.user
    #     return self.queryset.filter(user=user)


@login_required
def list_files(request):
    options = IRODSOptions(request.GET.get('host'), int(request.GET.get('port')), request.GET.get('username'),
                           request.GET.get('password'), request.GET.get('zone'))
    irods = IRODS(options)

    request.session['irods_username'] = options.user
    request.session['irods_host'] = options.host
    request.session['irods_port'] = options.port
    request.session['irods_zone'] = options.zone
    request.session['irods_path'] = request.GET.get('path', None)

    try:
        files = irods.list(request.GET.get('path'))
    except FileNotFoundError:
        return HttpResponseNotFound('Path not found')

    return JsonResponse({
        'files': files
    })


@login_required
def get_connection_info(request):
    return JsonResponse({
        'username': request.session.get('irods_username', None),
        'host': request.session.get('irods_host', None),
        'port': request.session.get('irods_port', None),
        'zone': request.session.get('irods_zone', None),
        'path': request.session.get('irods_path', None)
    })
