from django.urls import path

from . import views

urlpatterns = [
    path(r'counts/', views.aggregate_counts),
    path(r'institutions/', views.institutions_info),
    path(r'timeseries/', views.aggregate_timeseries),
    path(r'timeseries/<username>/', views.user_timeseries),
    path(r'timeseries/<owner>/<name>/<branch>/', views.workflow_timeseries),
]
