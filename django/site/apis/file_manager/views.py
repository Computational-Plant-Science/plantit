import humanize
import json

from django.views import View
from django.http import Http404, HttpResponse
from django.core.exceptions import PermissionDenied

from .permissions import open_folder


# from django.core.files.storage import FileSystemStorage
# from django.shortcuts import render
# from django import forms
# from file_manager.fields import FileBrowserField
#
# class FileForm(forms.Form):
#     # Example form that only has a file browser
#     files = FileBrowserField("Dev",
#                              path = '/')
#
# def filepicker(request):
#     # Method based view that renders a form with only a file browser
#     if request.method == 'POST':
#         form = FileForm(request.POST)
#         if form.is_valid():
#             # Lists the files selected in the form.
#             print("Selected files: " + str(form.cleaned_data['files']))
#     else:
#         form = FileForm()
#     return render(request, 'file_manager/file.html', {'form': form})



class FileBrowserView(View):
    """
        Provides an ajax based file browser.

        settable variables:
        file_storage: Must be a valid FileSystemStorage class
    """

    def post(self,request, command):
        """
            Parses the ajax command request
        """
        if request.is_ajax():
            self.file_storage = open_folder(request.POST.get('storage_type'),
                                            request.POST.get('dir'),
                                            request.user)

            if(command == 'browse'):
                return self.browse(request)
            elif(command == 'upload'):
                return self.upload(request)
            else:
                raise Http404('Not a vaild command')
        else:
            raise Http404 ('Not a vaild ajax call')

    def browse(self,request):
        """
            ajax/browse/

            Responds to ajax requests to list the files of a directory. Requests
            must contain the 'dir' POST variable populated with the directory to list

            The returned HttPresponse is json of the following structure:

            {
                'dirs' : ['list', 'of', 'dirs'],
                'files': [
                    { 'name': 'file name',
                      'size': 'human readable file size' },
                ]
            }
        """
        if request.POST:
            (dirs,files) = self.file_storage.listdir("./")
            sizes = []

            for file in files:
                sizes.append( humanize.naturalsize(self.file_storage.size(file)) )
            context = { 'dirs': dirs,
                        'files': list(map(lambda f, s: {'name': f, 'size': s} ,files,sizes)) }

            return HttpResponse(json.dumps(context), content_type='application/json')
        else:
            raise Http404('No POST data')

    def upload(self,request):
        """
            ajax/upload

            Responds to ajax requests to uplaod files. Can handle mutiple
            files at once. Requests must contain the 'pwd' POST variable populated
            with the directory to store the uploaded files in.
        """

        files = request.FILES.getlist('file')

        if(not files):
            raise Http404

        for f in files:
            self.file_storage.save(f.name,f)

        return HttpResponse(status=204)
