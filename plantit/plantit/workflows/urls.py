from django.urls import path

from . import views

urlpatterns = [
    path(r'list_all/', views.list_all),
    path(r'<username>/', views.list_by_user),
    path(r'<username>/<name>/', views.get),
    path(r'<username>/<name>/validate/', views.validate),
]
