from django import forms
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

class SelectFilesWidget(forms.widgets.Widget):
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
