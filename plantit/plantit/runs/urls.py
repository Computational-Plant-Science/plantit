from django.urls import path

from . import views, consumers

urlpatterns = [
    path(r'', views.runs),
    path(r'get_total_count/', views.get_total_count),
    path(r'<username>/get_by_user/', views.get_by_user),
    path(r'<username>/get_by_user_and_workflow/<workflow>/<page>/', views.get_runs_by_user_and_workflow),
    path(r'<username>/get_delayed_by_user_and_workflow/<workflow>/', views.get_delayed_runs_by_user_and_workflow),
    path(r'<username>/get_repeating_by_user_and_workflow/<workflow>/', views.get_repeating_runs_by_user_and_workflow),
    path(r'<username>/remove_delayed/<workflow>/', views.remove_delayed),
    path(r'<username>/remove_repeating/<workflow>/', views.remove_repeating),
    path(r'<username>/toggle_repeating/<workflow>/', views.toggle_repeating),
    path(r'<id>/', views.run),
    path(r'<id>/output/<file>/', views.get_output_file),
    path(r'<id>/file_text/', views.get_file_text),
    path(r'<id>/thumbnail/', views.get_thumbnail),
    path(r'<id>/submission_logs/', views.get_submission_logs),
    path(r'<id>/container_logs/', views.get_container_logs),
    path(r'<id>/status/', views.status),
    path(r'<id>/cancel/', views.cancel),
    path(r'<id>/delete/', views.delete)
]

websocket_urlpatterns = [
    path(r'ws/runs/<username>/', consumers.RunConsumer.as_asgi())
]
