import humanize
import json

from django.views import View
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import Http404, HttpResponse

from django import forms
from file_manager.forms import FileForm

def filepicker(request):
    if request.method == 'POST':
        form = FileForm(request.POST)
        print("Form Valid: " + str(form.is_valid()))

        if form.is_valid():
            print("Selected files: " + str(form.cleaned_data['files']))
    else:
        form = FileForm()
    return render(request, 'file_manager/file.html', {'form': form})

class FileBrowserView(View):
    """
        Provides an ajax based file browser.

        settable variables:
        file_storage: Must be a valid FileSystemStorage class
    """
    file_storage = FileSystemStorage('./files/')

    def post(self,request, command):
        """
            Parses the ajax command request
        """
        if request.is_ajax():
            if(command == 'browse'):
                return self.browse(request)
            elif(command == 'upload'):
                return self.upload(request)
            else:
                raise Http404
        else:
            raise Http404

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
            dir = request.POST.get('dir')

            (dirs,files) = self.file_storage.listdir(dir)
            sizes = []

            for file in files:
                sizes.append( humanize.naturalsize(self.file_storage.size(dir + file)) )
            context = { 'dirs': dirs,
                        'files': list(map(lambda f, s: {'name': f, 'size': s} ,files,sizes)) }

            return HttpResponse(json.dumps(context), content_type='application/json')
        else:
            raise Http404

    def upload(self,request):
        """
            ajax/upload

            Responds to ajax requests to uplaod files. Can handle mutiple
            files at once. Requests must contain the 'pwd' POST variable populated
            with the directory to store the uploaded files in.
        """
        pwd = request.POST.get('pwd')
        files = request.FILES.getlist('file')

        if(not files or not pwd):
            raise Http404

        for f in files:
            self.file_storage.save(pwd + f.name,f)

        return HttpResponse(status=204)
