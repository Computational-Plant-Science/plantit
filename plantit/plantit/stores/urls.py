from django.urls import path

from . import views

urlpatterns = [
    path(r'share_directory/', views.share_directory),
    path(r'unshare_directory/', views.unshare_directory),
    path(r'get_shared_directories/', views.get_shared_directories),
    path(r'get_directories_shared/', views.get_directories_shared),
]