from django.conf.urls import url, include
from rest_framework import routers
from collection.api import views
router = routers.DefaultRouter()

router.register(r'', views.CollectionViewSet)
urlpatterns = [
    url(r'^api/', include(router.urls)),
]
