from django.urls import path, include
from . import views

app_name = "workflows"
urlpatterns = [
    path('', views.list_workflows, name="list"),
]
