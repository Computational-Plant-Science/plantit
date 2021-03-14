from django.conf.urls import url, include
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic import RedirectView
from rest_framework import routers

from django.urls import path

from .auth.views import login_view, logout_view
from .miappe.views import *
from .clusters.views import ClustersViewSet
from .sessions.consumers import SessionConsumer
from .users.views import UsersViewSet, IDPViewSet
from .runs.consumers import RunConsumer
from .notifications.consumers import NotificationConsumer

router = routers.DefaultRouter()
router.register('users', UsersViewSet)
router.register('idp', IDPViewSet, basename='idp')
router.register('clusters', ClustersViewSet)
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
    url('runs/', include("plantit.runs.urls")),
    url('sessions/', include("plantit.sessions.urls")),
    url('workflows/', include("plantit.workflows.urls")),
    url('collections/', include("plantit.collections.urls")),
    url('notifications/', include("plantit.notifications.urls")),
    url('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon.ico'))),
]

websocket_urlpatterns = [
    path(r'ws/runs/<username>/', RunConsumer.as_asgi()),
    path(r'ws/notifications/<username>/', NotificationConsumer.as_asgi()),
    path(r'ws/sessions/<username>/<cluster>/', SessionConsumer.as_asgi())
]
