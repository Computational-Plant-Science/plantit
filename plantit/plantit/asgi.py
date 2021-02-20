import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from plantit.runs.urls import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plantit.settings")

asgi_app = get_asgi_application()
application = ProtocolTypeRouter({
    "http": asgi_app,
    "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
})
