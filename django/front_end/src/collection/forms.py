from django import forms
from plantit.collection.models import Collection
from plantit.file_manager.fields import FileBrowserField
from plantit.file_manager.filesystems.storage import AbstractStorageType
from plantit.file_manager.filesystems import registrar

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
        fields = ['name','description','storage_type','base_file_path']
