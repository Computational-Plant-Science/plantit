from django.urls import path, include

from . import views

urlpatterns = [
    path(r'', views.storage_types),
    path(r'lsdir/', views.folder, name='browse'),
    path(r'upload/',views.upload, name='upload'),
]
