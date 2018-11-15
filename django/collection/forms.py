from django import forms
from collection.images import Images2D
from file_manager.fields import FileBrowserField
from file_manager.filesystems.storage import AbstractStorageType

class CollectionFileForm(forms.Form):
    def __init__(self, storage_type, base_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'] =  FileBrowserField(storage_type,base_path)

class NewCollectionForm(forms.ModelForm):
    storage_type = forms.ChoiceField()
    base_file_path = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        storage_types = AbstractStorageType.objects.all()
        self.fields['storage_type'].choices = [(x.name,x.name) for x in storage_types]

    class Meta:
        model = Images2D
        fields = ['name','description','tags','storage_type','base_file_path']
