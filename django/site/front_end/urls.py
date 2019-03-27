from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index),
    path('jobs/', include('front_end.job_manager.urls')),
    path('workflows/', include('front_end.workflows.urls')),
    path('filemanager/', include('front_end.file_manager.urls')),
    path('collection/', include('front_end.collection.urls')),
    path('user/', include('front_end.user.urls'))
]
