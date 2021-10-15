from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.list_public),
    path(r'<owner>/', views.list_personal),
    path(r'<owner>/<name>/', views.get),
    path(r'<owner>/<name>/search/', views.search),
    path(r'<owner>/<name>/refresh/', views.refresh),
    path(r'<owner>/<name>/readme/', views.readme),
    path(r'<owner>/<name>/public/', views.toggle_public),
    path(r'<owner>/<name>/bind/', views.bind),
    path(r'<owner>/<name>/unbind/', views.unbind),
    path(f'<owner>/<name>/branches/', views.branches)
]
