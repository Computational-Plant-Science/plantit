import posixpath

from django.http import JsonResponse, Http404, HttpResponse
from django.contrib.auth.decorators import login_required

from plantit.stores import registrar
from plantit.stores.permissions import open_folder

"""
    Defines a RESTFUL API for interacting with the file manager
"""

@login_required
def storage_types(request):
    """
        List registered storage types

        **url:** `/apis/v1/files/`

        **Response Data:**
        A javascript object containing the attribute "storage_types", which
        holds a list of names of the avilable storage types.

        Example:
            .. code-block:: javascript

                {"storage_types": ["irods", "local"]}

        **Requires:** User must be logged in.
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

        **GET Parameters:**
            - path (str): the path to the folder
            - storage_type (str): The storage system the folder is on. Must be
              in the list provided by :meth:`storage_types`

        **url:** `/apis/v1/files/lsdir/?path=<path>&storage_type=<storage_type>`

        **Response Data:** A list files/folders at the path in the format
            required by jsTree  (https://www.jstree.com/docs/json/)

        **Requires:** User must be logged in.

        Example:
            .. code-block:: javascript

                [{
                    "text": "test_model_1",
                    "path": "/tempZone/home/rods/test_model_1",
                    "icon": "far fa-folder"
                 },
                 {
                    "text": "24-74-2.png",
                    "size": 7883,
                    "path": "/tempZone/home/rods/24-74-2.png",
                    "isLeaf": true, "icon": "far fa-file"
                }]
    """

    if not 'path' in request.GET:
        raise Http404("path required, not in GET data")

    if not 'storage_type' in request.GET:
        raise Http404("storage_type required, not in GET data")

    path = request.GET['path']
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
        Responds to ajax requests to upload files. Can handle multiple
        files at once.

        **POST Parameters:**
            - path (str): the path to the folder
            - storage_type (str): The storage system the folder is on. Must be
              in the list provided by :meth:`storage_types`

        **url:** `/apis/v1/files/upload/`

        **Response Data:** HTTP Server response.

        **Requires:** User must be logged in.
    """
    if not 'path' in request.POST:
        raise Http404("path required, not in POST data")

    if not 'storage_type' in request.POST:
        raise Http404("storage_type required, not in POST data")

    file_storage = open_folder(request.POST['storage_type'],
                               request.POST['path'],
                               request.user)

    files = request.FILES.getlist('file')

    if not files:
        raise Http404

    file_names = []
    for f in files:
        file_names.append(file_storage.save(f.name,f))

    return JsonResponse(file_names, safe=False)
