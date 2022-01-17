from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.submit_feedback),
    # path(r'tutorials/', views.download_tutorials),
    # path(r'feedback/', views.download_feedback_form),
]