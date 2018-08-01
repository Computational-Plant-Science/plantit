from django import forms
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

class FileBrowserWidget(forms.widgets.Widget):
    """
        Provides a ajax file browser
    """
    class Media:
        js = ("https://cdn.jsdelivr.net/npm/js-cookie@2/src/js.cookie.min.js",
              "https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js",
              'file_manager/js/browser.js',
              'file_manager/js/jquery.dm-uploader.js' )
        css = {
            'all' : ('file_manager/css/jquery.dm-uploader.css', )
        }

    def __init__(self, *args, **kwargs):
        super(forms.widgets.Widget, self).__init__(*args, **kwargs)
        self.attrs = {}

    def render(self, name, value, attrs=None, renderer=None):
        template_name = 'file_manager/file_list.html'

        return mark_safe(render_to_string(template_name,{}))

    def value_from_datadict(self, data, files, name):
        return data.getlist(name)

class UploadFilesWidget(forms.widgets.Widget):
    """
        Provides the abililty to upload files via ajax
    """
    template_name = 'file_manager/file_upload.html'

    class Media:
        js = ("https://cdn.jsdelivr.net/npm/js-cookie@2/src/js.cookie.min.js",
              "https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js",
              'file_manager/js/uploader-config.js',
              'file_manager/js/uploader-ui.js',
              'file_manager/js/jquery.dm-uploader.js' )
        css = {
            'all' : ('file_manager/css/jquery.dm-uploader.css',
                     'file_manager/css/uploader.css')
        }

    def __init__(self, *args, **kwargs):
        super(forms.widgets.Widget, self).__init__(*args, **kwargs)
        self.attrs = {}

    def value_from_datadict(self, data, files, name):
        return files.get(name)
