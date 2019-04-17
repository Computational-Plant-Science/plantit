import json
import posixpath

from django.http import JsonResponse, Http404, HttpResponse
from django.contrib.auth.decorators import login_required

from plantit.file_manager.permissions import open_folder
from plantit.file_manager.filesystems import registrar

"""
    Defines a RESTFUL API for interacting with the file manager
"""

@login_required
def storage_types(request):
    """
        List registered storage types

        Args:
            request: the HTTP request
    """

    context = {
        "storage_types" : list(registrar.list.keys()),
    }

    return JsonResponse(context)

@login_required
def folder(request):
    """
        List files in a folder in the format required by
        jsTree  (https://www.jstree.com/docs/json/)

        Args:
            request: the HTTP request
    """

    if not 'path' in request.GET:
        raise Http404("base_path required not in GET data")

    if not 'storage_type' in request.GET:
        raise Http404("storage_type required not in GET data")

    path = request.GET['path'].lstrip("/")
    storage_type = request.GET['storage_type']

    file_storage = open_folder(storage_type,
                                    path,
                                    request.user)

    (dirs,files) = file_storage.listdir('.')
    sizes = []

    for file in files:
        sizes.append( file_storage.size(file) )

    context = [
                {
                    "text" : dir,
                    "path" : posixpath.join(path,dir),
                    "icon" : "far fa-folder"
                } for dir in dirs
              ] + [
                {
                    "text" : file,
                    "size" : size,
                    "path" : posixpath.join(path,str(file)),
                    "isLeaf" : True,
                    "icon": "far fa-file"
                } for file,size in zip(files, sizes)
              ]

    return JsonResponse(context,safe=False)

@login_required
def upload(request):
    """
        ajax/upload

        Responds to ajax requests to uplaod files. Can handle mutiple
        files at once.
    """
    if not 'path' in request.POST:
        raise Http404("path required not in POST data")

    if not 'storage_type' in request.POST:
        raise Http404("storage_type required not in POST data")

    file_storage = open_folder(request.POST['storage_type'],
                               request.POST['path'],
                               request.user)

    files = request.FILES.getlist('file')

    if(not files):
        raise Http404

    file_names = []
    for f in files:
        file_names.append(file_storage.save(f.name,f))

    return JsonResponse(file_names,safe=False)
