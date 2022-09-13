from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.list),
    path(r'<name>/', views.get),
    path(r'<name>/exists/', views.exists),
    path(r'<name>/health/', views.healthcheck),
    path(r'<name>/checks/', views.healthchecks),
    path(r'<name>/policies/', views.policies),
]