from django.urls import path, include

from . import views

urlpatterns = [
    path(r'', views.workflows),
    path(r'<workflow>/', views.parameters),
    path(r'<workflow>/submit/<pk>/', views.submit)
]
