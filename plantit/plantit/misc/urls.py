from django.urls import path

from . import views

urlpatterns = [
    path(r'contributors/', views.contributors),
    path(r'maintenance/', views.maintenance_windows),
    path(r'updates/', views.updates),
]