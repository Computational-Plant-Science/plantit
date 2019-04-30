from os.path import join, basename, dirname
from .permissions import open_folder
from django.http import StreamingHttpResponse
from django.core.files.storage import FileSystemStorage


def download_stream(storage_type, filepath, user, *kwargs):
    '''
        Creates a downloadable stream to a file.
        File permissions are respected.

        Args:
            storage_type (str): name of the file system storage type must be
                subclass of AbstractStorageType
            path: path to file
            user: User that has permission to the folder path
            *kwargs: unique paramaters for each STORAGE type

    '''
    directory = dirname(filepath)
    filename = basename(filepath)

    storage = open_folder(storage_type, directory, user, *kwargs)
    file = storage.open(filename)

    response = StreamingHttpResponse(streaming_content=file)
    response['Content-Disposition'] = 'attachement; filename=%s'%(filename)
    return response
