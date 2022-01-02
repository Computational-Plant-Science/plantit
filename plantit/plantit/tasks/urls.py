from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.get_all_or_create),
    path(r'<owner>/', views.get_by_owner),
    path(r'<owner>/delayed/', views.get_delayed_by_owner),
    path(r'<owner>/repeating/', views.get_repeating_by_owner),
    path(r'<owner>/<name>/', views.get_by_owner_and_name),
    path(r'<owner>/<name>/exists/', views.exists),
    path(r'<owner>/<name>/status/', views.status),
    path(r'<owner>/<name>/cancel/', views.cancel),
    path(r'<owner>/<name>/delete/', views.delete),
    path(r'<owner>/<name>/output/', views.get_output_file),
    # path(r'<owner>/<name>/file_text/', views.get_file_text),
    # path(r'<owner>/<name>/3d_model/', views.get_3d_model),
    path(r'<owner>/<name>/agent_logs/', views.get_agent_logs),
    path(r'<owner>/<name>/agent_logs_content/', views.get_agent_logs_content),
    path(r'<owner>/<name>/scheduler_logs/', views.get_scheduler_logs),
    path(r'<owner>/<name>/scheduler_logs_content/', views.get_scheduler_logs_content),
    path(r'<owner>/<name>/orchestrator_logs/', views.get_task_logs),
    path(r'<owner>/<name>/orchestrator_logs_content/', views.get_task_logs_content),
    path(r'<owner>/<name>/transfer/', views.transfer_to_cyverse),
    path(r'search/<owner>/<workflow_name>/<page>/', views.search),
]
