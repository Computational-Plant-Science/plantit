from django.conf.urls import url, include
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic import RedirectView
from rest_framework import routers

from .auth.views import login_view, logout_view
from .miappe.views import *
from .targets.views import TargetsViewSet
from .users.views import UsersViewSet, IDPViewSet

router = routers.DefaultRouter()
router.register('users', UsersViewSet)
router.register('idp', IDPViewSet, basename='idp')
router.register('servers', TargetsViewSet)
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
    url('workflows/', include("plantit.workflows.urls")),
    url('stores/', include("plantit.stores.urls")),
    url('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon.ico'))),
]
