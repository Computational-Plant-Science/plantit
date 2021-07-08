from django.conf.urls import url, include
from django.conf.urls.static import static
from django.urls import path
from rest_framework import routers

from .auth.views import login_view, logout_view
from .miappe.views import *
from .notifications.consumers import NotificationConsumer
from .tasks.consumers import TaskConsumer
from .users.views import UsersViewSet, IDPViewSet

router = routers.DefaultRouter()

# user info and auth
router.register('users', UsersViewSet)
router.register('idp', IDPViewSet, basename='idp')

urlpatterns = [
                  url('', include(router.urls)),
                  url('auth/login/', login_view),
                  url('auth/logout/', logout_view),
                  url('agents/', include("plantit.agents.urls")),
                  url('datasets/', include("plantit.datasets.urls")),
                  url('workflows/', include("plantit.workflows.urls")),
                  url('tasks/', include("plantit.tasks.urls")),
                  url('stats/', include("plantit.stats.urls")),
                  url('notifications/', include("plantit.notifications.urls")),
                  url('feedback/', include("plantit.feedback.urls")),
                  url('miappe/', include("plantit.miappe.urls")),
              ] + static(r'/favicon.ico', document_root='static/favicon.ico')

websocket_urlpatterns = [
    path(r'ws/tasks/<username>/', TaskConsumer.as_asgi()),
    path(r'ws/notifications/<username>/', NotificationConsumer.as_asgi()),
]
