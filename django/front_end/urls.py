from django.contrib import admin
from django.urls import path, include
from .src.plantit import views

urlpatterns = [
    path('', views.index),
    path('jobs/', include('front_end.src.job_manager.urls')),
    path('workflows/', include('front_end.src.workflows.urls')),
    path('collection/', include('front_end.src.collection.urls')),
    path('user/', include('front_end.src.user.urls'))
]
