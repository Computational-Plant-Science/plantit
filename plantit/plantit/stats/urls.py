from django.urls import path

from . import views

urlpatterns = [
    path(r'counts/', views.counts),
]
