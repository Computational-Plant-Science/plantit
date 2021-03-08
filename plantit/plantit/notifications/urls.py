from django.urls import path

from . import views, consumers

urlpatterns = [
    path(r'<username>/get_by_user/', views.get_by_user),
    path(r'<username>/mark_read/', views.mark_read)
]
