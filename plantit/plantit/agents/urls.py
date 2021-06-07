from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.search_or_add),
    path(r'<name>/', views.get_by_name),
    path(r'<name>/exists/', views.exists),
    path(r'<host>/host_exists/', views.host_exists),
    path(r'<name>/public/', views.toggle_public),
    path(r'<name>/health/', views.healthcheck),
    path(r'<name>/policies/', views.get_access_policies),
    path(r'<name>/request/', views.request_access),
    path(r'<name>/revoke/', views.revoke_access),
    path(r'<name>/grant/', views.grant_access),
    path(r'<name>/keypair/', views.get_keypair)
]