from django.urls import path, include
from workflows import views

app_name = "workflows"
urlpatterns = [
    path('', views.list_workflows, name="list"),
    path('awesome_workflow/', include('workflows.awesome_workflow.django.urls'), name='awesome_workflow'),
    path('dirt2d/', include('workflows.DIRT2D.django.urls'), name='dirt2d')
]
