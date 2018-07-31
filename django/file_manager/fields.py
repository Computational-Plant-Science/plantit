from django import forms
from .widgets import FileBrowserWidget, UploadFilesWidget

class FileBrowserField(forms.Field):
    widget = FileBrowserWidget

    def __init__(self, require_all_fields=True, **kwargs):
        self.require_all_fields = require_all_fields
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
