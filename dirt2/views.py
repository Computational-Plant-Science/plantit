from .forms import FileForm
from file_manager.views import FileBrowserView
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

def filepicker(request):
    """
      Method based view that renders a form with only a file browser
    """
    if request.method == 'POST':
        form = FileForm(request.POST)
        if form.is_valid():
            """
              Lists the files selected in the form.
            """
            print("Selected files: " + str(form.cleaned_data['files']))
    else:
        form = FileForm()
    return render(request, 'file_manager/file.html', {'form': form})

@method_decorator(login_required, name='upload')
@method_decorator(login_required, name='browse')
class ChooseFileView(FileBrowserView):
  """
    Handles the file browser ajax requests.
  """
  file_storage = FileSystemStorage('./files/')
