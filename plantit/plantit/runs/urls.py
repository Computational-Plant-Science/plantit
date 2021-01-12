from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.runs),
    path(r'get_total_count/', views.get_total_count),
    path(r'<username>/get_by_user/<page>/', views.get_runs_by_user),
    path(r'<id>/', views.run),
    path(r'<id>/outputs/', views.list_outputs),
    path(r'<id>/output/<file>/', views.get_output_file),
    path(r'<id>/thumbnail/<file>/', views.get_thumbnail),
    path(r'<id>/logs/', views.get_logs),
    path(r'<id>/logs_text/<size>/', views.get_logs_text),
    path(r'<id>/status/', views.status)
]
