from django import forms
from collection.models import Collection
from file_manager.fields import FileBrowserField
from file_manager.filesystems.storage import AbstractStorageType
from file_manager.filesystems import registrar

class CollectionFileForm(forms.Form):
    def __init__(self, storage_type, base_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'] =  FileBrowserField(storage_type,base_path)

class NewCollectionForm(forms.ModelForm):
    storage_type = forms.ChoiceField()
    base_file_path = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['storage_type'].choices = [(x,x) for x in registrar.list.keys()]

    class Meta:
        model = Collection
        fields = ['name','description','tags','storage_type','base_file_path']
