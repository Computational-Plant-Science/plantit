from django.urls import path

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
    path(r'<owner>/<name>/3d_model/', views.get_3d_model),
    path(r'<owner>/<name>/task_logs/', views.get_task_logs),
    path(r'<owner>/<name>/container_logs/', views.get_container_logs),
    path(r'search/<owner>/<workflow_name>/<page>/', views.search),
]

websocket_urlpatterns = [
    path(r'ws/tasks/<username>/', consumers.TaskConsumer.as_asgi())
]
