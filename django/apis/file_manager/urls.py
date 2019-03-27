from django.urls import path, include

from .views import FileBrowserView
#from .views import filepicker

app_name = "file_manager"

urlpatterns = [
    path('ajax/<command>/', FileBrowserView.as_view(),name='ajax'),
    #path('', filepicker)
]
