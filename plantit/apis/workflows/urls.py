from django.urls import path, include

from . import views

urlpatterns = [
    path(r'', views.workflows),
    path(r'<workflow>/', views.workflow),
    path(r'<workflow>/submit/<pk>/', views.submit)
]
