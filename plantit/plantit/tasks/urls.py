from django.urls import path

from . import views

urlpatterns = [
    path(r'search/<owner>/<workflow_name>/<page>/', views.search),
    path(r'', views.get_or_create),
    path(r'delayed/', views.get_delayed),
    path(r'repeating/', views.get_repeating),
    path(r'triggered/', views.get_triggered),
    path(r'<guid>/', views.get_task),
    path(r'<guid>/exists/', views.exists),
    path(r'<guid>/cancel/', views.cancel),
    path(r'<guid>/complete/', views.complete),
    path(r'<guid>/output/dl/', views.download_output_file),
    path(r'<guid>/unschedule_delayed/', views.unschedule_delayed),
    path(r'<guid>/unschedule_repeating/', views.unschedule_repeating),
    path(r'<guid>/unschedule_triggered/', views.unschedule_triggered),
    # path(r'<guid>/file_text/', views.get_file_text),
    # path(r'<guid>/3d_model/', views.get_3d_model),
    path(r'<guid>/logs/agent/', views.get_agent_logs),
    path(r'<guid>/logs/agent/dl/', views.download_agent_logs),
    path(r'<guid>/logs/scheduler/', views.get_scheduler_logs),
    path(r'<guid>/logs/scheduler/dl/', views.download_scheduler_logs),
    path(r'<guid>/logs/orchestrator/', views.get_task_logs),
    path(r'<guid>/logs/orchestrator/dl/', views.download_task_logs),
]
