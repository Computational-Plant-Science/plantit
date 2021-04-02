from django.urls import path

from . import views

urlpatterns = [
    path(r'list_all/', views.list_all),
    path(r'refresh_all/', views.refresh_all),
    path(r'<username>/', views.list_by_user),
    path(r'<username>/<name>/', views.get),
    path(r'<username>/<name>/refresh/', views.refresh),
    path(r'<username>/<name>/validate/', views.validate),
]
