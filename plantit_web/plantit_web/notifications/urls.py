from django.urls import path

from . import views

urlpatterns = [
    path(r'<owner>/', views.list_by_user),
    path(r'<owner>/<guid>/', views.get_or_dismiss)
]
