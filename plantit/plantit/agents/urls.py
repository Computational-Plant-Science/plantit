from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.list_or_bind),
    path(r'<name>/', views.get_or_unbind),
    path(r'<name>/exists/', views.exists),
    path(r'<host>/host_exists/', views.host_exists),
    path(r'<name>/public/', views.toggle_public),
    path(r'<name>/disable/', views.toggle_disabled),
    path(r'<name>/health/', views.healthcheck),
    path(r'<name>/policies/', views.get_access_policies),
    path(r'<name>/auth/', views.set_authentication_strategy),
    path(r'<name>/authorize_user/', views.authorize_user),
    path(r'<name>/unauthorize_user/', views.unauthorize_user),
    path(r'<name>/authorize_workflow/', views.authorize_workflow),
    path(r'<name>/unauthorize_workflow/', views.unauthorize_workflow),
    path(r'<name>/block_workflow/', views.block_workflow),
    path(r'<name>/unblock_workflow/', views.unblock_workflow),
]