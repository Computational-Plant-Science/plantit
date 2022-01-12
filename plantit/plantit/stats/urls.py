from django.urls import path

from . import views

urlpatterns = [
    path(r'totals/', views.total_counts),
    path(r'timeseries/', views.total_timeseries),
    path(r'institutions/', views.institutions_info),
    path(r'workflow_timeseries/<owner>/<name>/<branch>/', views.workflow_timeseries)
]
