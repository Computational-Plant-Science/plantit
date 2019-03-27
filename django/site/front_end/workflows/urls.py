from django.urls import path, include
from workflows import views

app_name = "workflows"
urlpatterns = [
    path('', views.list_workflows, name="list"),
]
