from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.runs),
    path(r'get_total_count/', views.get_total_count),
    path(r'<username>/get_by_user/<page>/', views.get_runs_by_user),
    path(r'<username>/get_by_user_and_flow/<flow>/<page>/', views.get_runs_by_user_and_flow),
    path(r'<username>/get_delayed_by_user_and_flow/<flow>/', views.get_delayed_runs_by_user_and_flow),
    path(r'<username>/get_repeating_by_user_and_flow/<flow>/', views.get_repeating_runs_by_user_and_flow),
    path(r'<username>/remove_delayed/<flow>/', views.remove_delayed),
    path(r'<username>/remove_repeating/<flow>/', views.remove_repeating),
    path(r'<username>/toggle_repeating/<flow>/', views.toggle_repeating),
    path(r'<id>/', views.run),
    path(r'<id>/outputs/', views.list_outputs),
    path(r'<id>/output/<file>/', views.get_output_file),
    path(r'<id>/thumbnail/<file>/', views.get_thumbnail),
    path(r'<id>/submission_logs/', views.get_submission_logs),
    path(r'<id>/container_logs/', views.get_container_logs),
    path(r'<id>/status/', views.status),
    path(r'<id>/cancel/', views.cancel)
]

websocket_urlpatterns = [
    path(r'ws/run/<id>/', views.RunConsumer.as_asgi()),
]
