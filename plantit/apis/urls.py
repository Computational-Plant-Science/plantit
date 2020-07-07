from django.conf.urls import url, include
from rest_framework import routers

from .collection.views import CollectionViewSet, SampleViewSet, list_files, get_connection_info
from .runs.views import RunViewSet, download_results, get_run
from .user.views import ProfileViewSet
from .auth.views import login_view, logout_view

router = routers.DefaultRouter()
router.register('runs', RunViewSet)
router.register('collections', CollectionViewSet)
router.register('samples', SampleViewSet)
router.register('profiles', ProfileViewSet)
urlpatterns = [
    url('files/', include("apis.stores.urls")),
    url('pipelines/', include("apis.pipelines.urls")),
    url('clusters/', include("apis.clusters.urls")),
    url('auth/login/', login_view),
    url('auth/logout/', logout_view),
    url(r'runs/(?P<pk>\d+)/download_results/', download_results),
    url(r'runs/(?P<id>\d+)/', get_run),
    url(r'collections/list_files/', list_files),
    url(r'collections/connection_info/', get_connection_info),
    # url(r'github_request_identity/', github_request_identity, name='github_request_identity'),
    # url(r'github_handle_temporary_code/', github_handle_temporary_code, name='github_handle_temporary_code'),
    url('', include(router.urls))
]
