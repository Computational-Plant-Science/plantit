from django.conf.urls import url, include
from rest_framework import routers

from .datasets.views import CollectionViewSet
from .users.views import ProfileViewSet
from .auth.views import login_view, logout_view

router = routers.DefaultRouter()
router.register('collections', CollectionViewSet)
router.register('profiles', ProfileViewSet)
urlpatterns = [
    url('pipelines/', include("apis.workflows.urls")),
    url('runs/', include("apis.runs.urls")),
    url('clusters/', include("apis.targets.urls")),
    url('collections/', include("apis.datasets.urls")),
    url('auth/login/', login_view),
    url('auth/logout/', logout_view),
    url('', include(router.urls))
]
