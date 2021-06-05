from django.urls import path

from . import views, consumers

urlpatterns = [
    path(r'', views.list_public),
    path(r'<owner>/', views.list_personal),
    path(r'<owner>/<name>/', views.get),
    path(r'<owner>/<name>/search/', views.search),
    path(r'<owner>/<name>/refresh/', views.refresh),
    path(r'<owner>/<name>/readme/', views.readme),
    path(r'<owner>/<name>/public/', views.toggle_public),
    path(r'<owner>/<name>/connect/', views.connect),
    path(r'<owner>/<name>/disconnect/', views.disconnect),
]

websocket_urlpatterns = [
    path(r'ws/workflows/<owner>/', consumers.WorkflowConsumer.as_asgi())
]
