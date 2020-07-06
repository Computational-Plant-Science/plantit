from django.urls import path, include

from . import views

urlpatterns = [
    path(r'', views.list),
    path(r'<owner>/<name>/', views.get)
]
