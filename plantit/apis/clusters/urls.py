from django.urls import path

from apis.clusters import views


urlpatterns = [
    path(r'', views.clusters)
]