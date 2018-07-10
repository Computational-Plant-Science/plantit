from django import forms
from .widgets import SelectFilesWidget

class FilesField(forms.Field):
    widget = SelectFilesWidget

    def __init__(self, require_all_fields=True, **kwargs):
        self.require_all_fields = require_all_fields
        super().__init__(**kwargs)

    def clean(self, value):
        return value

    def validate(self, value):
        super().validate(value)
