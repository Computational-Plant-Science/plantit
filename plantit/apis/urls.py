from django.conf.urls import url, include
from rest_framework import routers

from .collection.views import CollectionViewSet, SampleViewSet
from .jobs.views import JobViewSet, download_results
from .user.views import ProfileViewSet
from .auth.views import login_view, logout_view

router = routers.DefaultRouter()
router.register('jobs', JobViewSet)
router.register('collections', CollectionViewSet)
router.register('samples', SampleViewSet)
router.register('profiles', ProfileViewSet)
urlpatterns = [
    url('files/', include("apis.stores.urls")),
    url('workflows/', include("apis.workflows.urls")),
    url('clusters/', include("apis.clusters.urls")),
    url('auth/login/', login_view),
    url('auth/logout/', logout_view),
    url(r'jobs/(?P<pk>\d+)/download_results/', download_results),
    # url(r'github_request_identity/', github_request_identity, name='github_request_identity'),
    # url(r'github_handle_temporary_code/', github_handle_temporary_code, name='github_handle_temporary_code'),
    url('', include(router.urls))
]
