from django.urls import path

from . import views

urlpatterns = [
    path(r'current/', views.get),
    path(r'start/', views.start),
    path(r'stop/', views.stop),
]