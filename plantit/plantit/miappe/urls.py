from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.list_or_create),
    path(r'<owner>/', views.list_by_owner),
    path(r'<owner>/<title>/', views.get_or_delete),
    path(r'<owner>/<title>/exists/', views.exists),
    path(r'<owner>/<title>/add_team_member/', views.add_team_member),
    path(r'<owner>/<title>/remove_team_member/', views.remove_team_member),
    path(r'<owner>/<title>/add_study/', views.add_study),
    path(r'<owner>/<title>/remove_study/', views.remove_study),
]