import os
import logging

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plantit.settings")
asgi_app = get_asgi_application()

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from plantit_web.urls import websocket_urlpatterns

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

application = ProtocolTypeRouter({
    "http": asgi_app,
    "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
})
