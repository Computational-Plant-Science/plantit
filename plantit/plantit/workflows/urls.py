from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.list_all),
    path(r'<username>/', views.list),
    path(r'<username>/<name>/', views.get),
]
