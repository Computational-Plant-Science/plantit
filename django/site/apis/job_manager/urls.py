from django.conf.urls import url, include
from rest_framework import routers
from job_manager.api import views
router = routers.DefaultRouter()

router.register(r'jobs', views.JobViewSet)
urlpatterns = [
    url(r'^api/', include(router.urls)),
]
