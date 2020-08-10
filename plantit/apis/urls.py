from django.conf.urls import url, include
from rest_framework import routers

from .collection.views import CollectionViewSet
from .user.views import ProfileViewSet
from .auth.views import login_view, logout_view

router = routers.DefaultRouter()
router.register('collections', CollectionViewSet)
router.register('profiles', ProfileViewSet)
urlpatterns = [
    url('pipelines/', include("apis.pipelines.urls")),
    url('runs/', include("apis.runs.urls")),
    url('clusters/', include("apis.clusters.urls")),
    url('collections/', include("apis.collection.urls")),
    url('auth/login/', login_view),
    url('auth/logout/', logout_view),
    url('', include(router.urls))
]
