from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.list_or_create),
    path(r'<owner>/', views.list_by_owner),
    path(r'<owner>/<id>/', views.get_by_owner_and_unique_id),
    path(r'<owner>/<id>/exists/', views.exists),
    path(r'<owner>/<id>/delete/', views.delete),
    path(r'<owner>/<id>/add_team_member/', views.add_team_member),
    path(r'<owner>/<id>/remove_team_member/', views.remove_team_member),
]