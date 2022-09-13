from django.conf.urls import url, include
from django.conf.urls.static import static
from django.urls import path, re_path
from rest_framework import routers
from rest_framework import permissions

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from .users.views import UsersViewSet, IDPViewSet
from .consumers import UserEventConsumer

router = routers.DefaultRouter()

# auth and users APIs are the only ViewSets, everything else is methods
router.register('users', UsersViewSet)
router.register('idp', IDPViewSet, basename='idp')

# Swagger config
schema_view = get_schema_view(
    openapi.Info(
        title="plantit API",
        default_version='v1',
        description="The plantit REST API.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="wbonelli@uga.edu"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
                  url('', include(router.urls)),
                  # rest of the APIs
                  url('agents/', include("plantit.agents.urls")),
                  url('datasets/', include("plantit.datasets.urls")),
                  url('workflows/', include("plantit.workflows.urls")),
                  url('tasks/', include("plantit.tasks.urls")),
                  url('stats/', include("plantit.stats.urls")),
                  url('misc/', include("plantit.misc.urls")),
                  url('notifications/', include("plantit.notifications.urls")),
                  url('feedback/', include("plantit.feedback.urls")),
                  url('miappe/', include("plantit.miappe.urls")),
                  # Swagger endpoints
                  re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
                  re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
                  re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
                  # why is favicon still not working ???
              ] + static(r'/favicon.ico', document_root='static/favicon.ico')

# route all push events through a single websocket, distinguishing types in the client
websocket_urlpatterns = [path(r'ws/<username>/', UserEventConsumer.as_asgi())]
