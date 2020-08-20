from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.runs),
    path(r'<id>/', views.run),
    path(r'<id>/status/', views.status)
]
