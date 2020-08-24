from django.conf.urls import url, include
from django.views.generic import RedirectView
from rest_framework import routers

from .targets.views import TargetsViewSet
from .users.users import UsersViewSet
from .auth.views import login_view, logout_view
from django.contrib.staticfiles.storage import staticfiles_storage

router = routers.DefaultRouter()
router.register('users', UsersViewSet)
router.register('targets', TargetsViewSet)

urlpatterns = [
    url('', include(router.urls)),
    url('auth/login/', login_view),
    url('auth/logout/', logout_view),
    url('runs/', include("plantit.runs.urls")),
    url('workflows/', include("plantit.workflows.urls")),
    url('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon.ico'))),
]
