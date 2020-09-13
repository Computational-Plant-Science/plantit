import django_cas_ng
from django.conf.urls import url, include
from django.views.generic import RedirectView
import django_cas_ng.views
from rest_framework import routers

from .miappe.views import *
from .targets.views import TargetsViewSet
from .users.views import UsersViewSet
from .auth.views import login_view, logout_view
from django.contrib.staticfiles.storage import staticfiles_storage

router = routers.DefaultRouter()
router.register('users', UsersViewSet)
router.register('targets', TargetsViewSet)
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
    url('accounts/callback/', django_cas_ng.views.CallbackView.as_view(), name='cas_ng_proxy_callback'),
    url('auth/login/', login_view),
    url('auth/logout/', logout_view),
    url('runs/', include("plantit.runs.urls")),
    url('workflows/', include("plantit.workflows.urls")),
    url('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon.ico'))),
]
