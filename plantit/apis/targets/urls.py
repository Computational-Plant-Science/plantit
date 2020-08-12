from django.urls import path

from apis.targets import views


urlpatterns = [
    path(r'', views.clusters)
]