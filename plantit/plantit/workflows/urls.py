from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.list),
    path(r'<username>/<name>/', views.get),
]
