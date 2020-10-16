from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.runs),
    path(r'<username>/get_by_user/', views.get_runs_by_user),
    path(r'<id>/', views.run),
    path(r'<id>/status/', views.status)
]
