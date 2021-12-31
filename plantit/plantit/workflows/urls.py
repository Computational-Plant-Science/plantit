from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.list_public),
    path(r'u/', views.list_user),
    path(r'o/', views.list_org),
    path(r'p/', views.list_project),
    path(r'<owner>/u/<name>/<branch>/', views.get),
    path(r'<owner>/u/<name>/<branch>/search/', views.search),
    path(r'<owner>/u/<name>/<branch>/refresh/', views.refresh),
    path(r'<owner>/u/<name>/<branch>/readme/', views.readme),
    path(f'<owner>/u/<name>/<branch>/branches/', views.branches)
]
