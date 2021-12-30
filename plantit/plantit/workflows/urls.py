from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.list_public),
    path(r'<member>/o/', views.list_org),
    path(r'<owner>/u/', views.list_personal),
    path(r'<owner>/c/', views.list_collaborator),
    path(r'<owner>/u/<name>/<branch>/', views.get),
    path(r'<owner>/u/<name>/<branch>/search/', views.search),
    path(r'<owner>/u/<name>/<branch>/refresh/', views.refresh),
    path(r'<owner>/u/<name>/<branch>/readme/', views.readme),
    path(f'<owner>/u/<name>/<branch>/branches/', views.branches)
]
