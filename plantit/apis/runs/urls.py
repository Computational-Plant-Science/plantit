from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.get_runs),
    path(r'<id>/', views.get_run),
    path(r'<id>/status/', views.get_status),
    path(r'<id>/update_target_status/', views.update_target_status),
    path(r'<id>/results/', views.get_results),
]
