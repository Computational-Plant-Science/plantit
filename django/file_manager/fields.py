from django import forms
from .widgets import FileBrowserWidget, UploadFilesWidget

class FileBrowserField(forms.Field):

    def __init__(self, storage_type, path, require_all_fields=True, **kwargs):
        self.require_all_fields = require_all_fields
        self.widget = FileBrowserWidget(storage_type = storage_type, path = path)
        super().__init__(**kwargs)

    def clean(self, value):
        return value

    def validate(self, value):
        super().validate(value)

class FileUploadField(forms.Field):
    widget = UploadFilesWidget

    def __init__(self, require_all_fields=True, **kwargs):
        self.require_all_fields = require_all_fields
        super().__init__(**kwargs)

    def clean(self, value):
        return value

    def validate(self, value):
        super().validate(value)
