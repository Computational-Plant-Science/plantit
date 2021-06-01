from django.urls import path

import plantit.runs.utils
from . import views, consumers

urlpatterns = [
    path(r'', views.get_all_or_create),
    path(r'<owner>/', views.get_by_owner),
    path(r'<owner>/<name>/', views.get_by_owner_and_name),
    path(r'<owner>/<name>/exists/', views.exists),
    path(r'<owner>/<name>/status/', views.status),
    path(r'<owner>/<name>/cancel/', views.cancel),
    path(r'<owner>/<name>/delete/', views.delete),
    path(r'<owner>/<name>/output/<file>/', views.get_output_file),
    path(r'<owner>/<name>/file_text/', views.get_file_text),
    path(r'<owner>/<name>/thumbnail/', views.get_thumbnail),
    path(r'<owner>/<name>/3d_model/', plantit.runs.utils.get_3d_model),
    path(r'<owner>/<name>/submission_logs/', views.get_submission_logs),
    path(r'<owner>/<name>/container_logs/', views.get_container_logs),
    path(r'search/<owner>/<workflow_name>/<page>/', views.search),
    path(r'search_delayed/<owner>/<workflow_name>/', views.search_delayed),
    path(r'search_repeating/<owner>/<workflow_name>/', views.search_repeating),
    # path(r'<owner>/<workflow_name>/remove_delayed', views.remove_delayed),  # TODO move to separate API (Schedules?)
    # path(r'<owner>/<workflow_name>/remove_repeating', views.remove_repeating),
    # path(r'<owner>/<workflow_name>/toggle_repeating', views.toggle_repeating),
    # path(r'get_total_count/', views.get_total_count),  # TODO move to separate Stats API
]

websocket_urlpatterns = [
    path(r'ws/runs/<username>/', consumers.RunConsumer.as_asgi())
]
