from django import forms

from .fields import FilesField

class FileForm(forms.Form):
    name = forms.CharField(max_length=30)
    files = FilesField()
