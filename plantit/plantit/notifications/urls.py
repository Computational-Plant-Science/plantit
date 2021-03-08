from django.urls import path

from . import views, consumers

urlpatterns = [
    path(r'<username>/get_by_user/', views.get_by_user)
]

websocket_urlpatterns = [
    path(r'ws/notification/<username>/', consumers.NotificationConsumer.as_asgi())
]