from django.urls import path, include

from . import views

urlpatterns = [
    path(r'', views.workflows),
    path(r'<owner>/<name>/', views.workflow)
]
