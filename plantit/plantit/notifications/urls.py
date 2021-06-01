from django.urls import path

from . import views, consumers

urlpatterns = [
    path(r'<owner>/', views.get_by_user),
    path(r'<owner>/mark_read/', views.mark_read)
]
