## Setup

forms.py:
```python
from django import forms
from file_manager.fields import FilesField

class FileForm(forms.Form):
    """
      Example form that only has a file browser
    """
    files = FilesField()
```

Two views are required for the file picker, one for the form and one to
support the ajax file browser commands

views.py:
```python
from file_manager.views import FileBrowserView
from django.core.files.storage import FileSystemStorage
from .forms import FileForm
from django.shortcuts import render

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

class FileFormView(FileBrowserView):
  """
    Handles the file browser ajax requests.
  """
  file_storage = FileSystemStorage('./')
```

For each file browser, a path needs to be added to urls.py. The path
can be anything you like, but must end in '/<command>/'

urls.py:
```python
from .views import FileFormView

urlpatterns = [
    ...,
    path('ajax/<command>/',FileFormView.as_view(),name='ajax')
]
```

## Authentication

Authentication can be added using django's built in class based view Authentication
techniques (https://docs.djangoproject.com/en/2.0/topics/class-based-views/intro/)

for example, to require authentication for uploading and browsing, decorate
the methods with the "login_required" decorator

views.py
```python
@method_decorator(login_required, name='upload')
@method_decorator(login_required, name='browse')
class ChooseFileView(FileBrowserView):
  """
    Handles the file browser ajax requests.
  """
  file_storage = FileSystemStorage('./files/')
```
