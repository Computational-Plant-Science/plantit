from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.list_public),
    path(r'<owner>/u/', views.list_personal),
    path(r'<member>/o/', views.list_org),
    path(r'<owner>/u/<name>/', views.get),
    path(r'<owner>/u/<name>/search/', views.search),
    path(r'<owner>/u/<name>/refresh/', views.refresh),
    path(r'<owner>/u/<name>/readme/', views.readme),
    path(r'<owner>/u/<name>/public/', views.toggle_public),
    path(r'<owner>/u/<name>/bind/', views.bind),
    path(r'<owner>/u/<name>/unbind/', views.unbind),
    path(f'<owner>/u/<name>/branches/', views.branches)
]
