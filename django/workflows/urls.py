from django.urls import path, include
from workflows import views
app_name = "workflows"
urlpatterns = [
    path('', views.list_workflows, name="list"),
    path('fake_workflow', include('workflows.fake_workflow.urls'), name="fake_workflow")
    #path('dirt2d/', include('workflows.dirt2d.urls'), name="dirt2d"),
]
