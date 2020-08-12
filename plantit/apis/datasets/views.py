from os.path import join

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseNotFound, StreamingHttpResponse
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated

from plantit.datasets.models import Dataset, DatasetMetadatum
from plantit.stores.irodsstore import IRODS, IRODSOptions
from .serializers import CollectionSerializer


class CollectionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)

    queryset = Dataset.objects.all()
    serializer_class = CollectionSerializer

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(user=user)


def to_json(dataset):
    return {
        "pk": dataset.pk,
        "name": dataset.name,
        "description": dataset.description,
        "base_file_path": dataset.base_file_path,
        "owner": dataset.user.username,
        "public": dataset.public
    }


@login_required
@api_view(['GET'])
def list_all(request):
    user = request.user
    if user.is_anonymous:
        community_datasets = Dataset.objects.filter(public=True)
        return JsonResponse({
            "community": [to_json(dataset) for dataset in community_datasets],
        })
    else:
        community_datasets = Dataset.objects.exclude(user=user).filter(public=True)
        user_datasets = Dataset.objects.filter(user=user)
        return JsonResponse({
            "community": [to_json(dataset) for dataset in community_datasets],
            "user": [to_json(dataset) for dataset in user_datasets]
        })


@login_required
@api_view(['GET'])
def list_by_owner(request, owner):
    user = User.objects.get(username=owner)
    return JsonResponse([to_json(dataset) for dataset in Dataset.objects.filter(user=user)])


@login_required
@api_view(['GET'])
def get_by_owner_and_name(request, owner, name):
    user = User.objects.get(username=owner)
    return JsonResponse(to_json(Dataset.objects.get(user=user, name=name)))


@login_required
@api_view(['POST'])
def create(request):
    user = request.user
    name = request.data['name']
    description = request.data['description']
    dataset = Dataset.objects.create(user=user, name=name, description=description, storage_type='irods',
                                     base_file_path=join(settings.IRODS_BASEPATH, user.username, name))
    return JsonResponse({
        'dataset': to_json(dataset)
    })


# @login_required
# @api_view(['POST'])
# def delete(request, owner, name):
#     user = request.user
#     name = request.data['name']
#     description = request.data['description']
#     dataset = Dataset.objects.create(user=user, name=name, description=description, storage_type='irods',
#                                         base_file_path=join(settings.IRODS_BASEPATH, user.username, name))
#     return JsonResponse({
#         'dataset': to_json(dataset)
#     })


@login_required
@api_view(['GET'])
def list_metadata(request, owner, name):
    user = User.objects.get(username=owner)
    dataset = Dataset.objects.get(user=user, name=name)
    metadata = DatasetMetadatum.objects.filter(dataset=dataset)
    return JsonResponse({
        'metadata': [{'key': metadatum.key, 'value': metadatum.value} for metadatum in metadata]
    })


@login_required
@api_view(['POST'])
def update_description(request, owner, name):
    user = User.objects.get(username=owner)
    dataset = Dataset.objects.get(user=user, name=name)
    dataset.description = request.data['description']
    dataset.save()
    return JsonResponse({
        'description': dataset.description
    })


@login_required
@api_view(['POST'])
def update_metadata(request, owner, name):
    user = User.objects.get(username=owner)
    dataset = Dataset.objects.get(user=user, name=name)
    metadata = request.data['metadata']
    DatasetMetadatum.objects.filter(dataset=dataset).delete()
    DatasetMetadatum.objects.bulk_create(
        [DatasetMetadatum(dataset=dataset, key=datum['key'], value=datum['value']) for datum in metadata])
    return JsonResponse({
        'metadata': metadata
    })


@login_required
@api_view(['GET'])
def list_files(request, owner, name):
    irods = IRODS(IRODSOptions(request.GET.get('host'),
                               int(request.GET.get('port')),
                               request.GET.get('username'),
                               request.GET.get('password'),
                               request.GET.get('zone')) if 'host' in request.GET else IRODSOptions(settings.IRODS_HOST,
                                                                                                   int(
                                                                                                       settings.IRODS_PORT),
                                                                                                   settings.IRODS_USERNAME,
                                                                                                   settings.IRODS_PASSWORD,
                                                                                                   settings.IRODS_ZONE))
    user = User.objects.get(username=owner)
    dataset = Dataset.objects.get(user=user, name=name)
    path = dataset.base_file_path

    try:
        files = irods.list(path)
    except FileNotFoundError:
        return HttpResponseNotFound('Path not found')

    return JsonResponse({
        'files': files
    })


@login_required
@api_view(['POST'])
def delete_files(request, owner, name):
    irods = IRODS(IRODSOptions(request.GET.get('host'),
                               int(request.GET.get('port')),
                               request.GET.get('username'),
                               request.GET.get('password'),
                               request.GET.get('zone')) if 'host' in request.GET else IRODSOptions(settings.IRODS_HOST,
                                                                                                   int(
                                                                                                       settings.IRODS_PORT),
                                                                                                   settings.IRODS_USERNAME,
                                                                                                   settings.IRODS_PASSWORD,
                                                                                                   settings.IRODS_ZONE))

    files = request.data['files']
    user = User.objects.get(username=owner)
    dataset = Dataset.objects.get(user=user, name=name)
    base_path = dataset.base_file_path

    try:
        for file in files:
            file_path = join(base_path, file)
            irods.delete(file_path)

        files = irods.list(base_path)
    except FileNotFoundError:
        return HttpResponseNotFound('Path not found')

    return JsonResponse({
        'files': files
    })


@login_required
@api_view(['POST'])
def upload_files(request, owner, name):
    irods = IRODS(IRODSOptions(request.data['host'],
                               int(request.data['port']),
                               request.data['username'],
                               request.data['password'],
                               request.data['zone']) if 'host' in request.data else IRODSOptions(settings.IRODS_HOST,
                                                                                                 int(
                                                                                                     settings.IRODS_PORT),
                                                                                                 settings.IRODS_USERNAME,
                                                                                                 settings.IRODS_PASSWORD,
                                                                                                 settings.IRODS_ZONE))
    user = User.objects.get(username=owner)
    dataset = Dataset.objects.get(user=user, name=name)
    path = dataset.base_file_path
    files = request.FILES.getlist('file')

    if not files:
        raise RuntimeError("no files provided")

    try:
        for file in files:
            files = irods.save(join(path, file.name), file)
    except FileNotFoundError:
        return HttpResponseNotFound('Path not found')

    return JsonResponse({
        'files': files
    })


@login_required
@api_view(['GET'])
def download_files(request, owner, name):
    irods = IRODS(IRODSOptions(request.data['host'],
                               int(request.data['port']),
                               request.data['username'],
                               request.data['password'],
                               request.data['zone']) if 'host' in request.data else IRODSOptions(settings.IRODS_HOST,
                                                                                                 int(
                                                                                                     settings.IRODS_PORT),
                                                                                                 settings.IRODS_USERNAME,
                                                                                                 settings.IRODS_PASSWORD,
                                                                                                 settings.IRODS_ZONE))
    user = User.objects.get(username=owner)
    dataset = Dataset.objects.get(user=user, name=name)
    path = dataset.base_file_path
    response = StreamingHttpResponse(streaming_content=irods.read(path))
    response['Content-Disposition'] = 'attachement; filename=%s' % (path)
    return response
