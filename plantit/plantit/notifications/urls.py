from django.urls import path

from . import views

urlpatterns = [
    path(r'<username>/get_by_user/', views.get_by_user)
]