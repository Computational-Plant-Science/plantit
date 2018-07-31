from django.urls import path, include
from job_manager import views

app_name = "job_manager"
urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('', include('job_manager.api.urls')),
    path('<int:job_pk>/submit_job/', views.submit_job, name='submit_job')
]
