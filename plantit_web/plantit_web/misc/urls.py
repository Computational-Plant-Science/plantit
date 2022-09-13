from django.urls import path

from . import views

urlpatterns = [
    path(r'updates/', views.updates),
    path(r'maintenance/', views.maintenance_windows),
]