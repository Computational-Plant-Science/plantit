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
router.register('users', UsersViewSet)
router.register('idp', IDPViewSet, basename='idp')
router.register('miappe/investigations', InvestigationViewSet)
router.register('miappe/studies', StudyViewSet)
router.register('miappe/roles', RoleViewSet)
router.register('miappe/files', FileViewSet)
router.register('miappe/biological_materials', BiologicalMaterialViewSet)
router.register('miappe/environment_parameters', EnvironmentParameterViewSet)
router.register('miappe/experimental_factors', ExperimentalFactorViewSet)
router.register('miappe/events', EventViewSet)
router.register('miappe/observation_units', ObservationUnitViewSet)
router.register('miappe/samples', SampleViewSet)
router.register('miappe/observed_variables', ObservedVariableViewSet)

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
              ] + static(r'/favicon.ico', document_root='static/favicon.ico')

websocket_urlpatterns = [
    path(r'ws/tasks/<username>/', TaskConsumer.as_asgi()),
    path(r'ws/notifications/<username>/', NotificationConsumer.as_asgi()),
]
