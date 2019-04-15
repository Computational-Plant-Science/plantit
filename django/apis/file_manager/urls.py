from django.urls import path, include

from . import views

urlpatterns = [
    path(r'', views.storage_types),
    path(r'<str:storage_type>', views.folder, name='browse'),
    path(r'<str:storage_type>/upload',views.upload, name='upload')
]
