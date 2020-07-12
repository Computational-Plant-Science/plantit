from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.list),
    path(r'<owner>/<name>/', views.get),
    path(r'start/', views.start)
]