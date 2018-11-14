from django import forms

from file_manager.fields import FileBrowserField

class CollectionFileForm(forms.Form):
    def __init__(self, storage_type, base_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'] =  FileBrowserField(storage_type,base_path)
