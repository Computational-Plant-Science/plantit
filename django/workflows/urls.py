from django.urls import path, include
from workflows import views

app_name = "workflows"
urlpatterns = [
    path('', views.list_workflows, name="list"),
    path('dirt2d/', include('workflows.dirt2d.django.urls'), name='dirt2d')
]
