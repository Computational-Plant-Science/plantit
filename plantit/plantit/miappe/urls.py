from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.list_all_investigations),
    path(r'<owner>/', views.list_investigations_by_owner),
    path(r'<owner>/<id>/', views.get_investigation),
    path(r'<owner>/<id>/exists/', views.investigation_exists),
    path(r'<owner>/<id>/delete/', views.delete_investigation),
    path(r'<owner>/<id>/add_team_member/', views.add_team_member),
    path(r'<owner>/<id>/remove_team_member/', views.remove_team_member),
]