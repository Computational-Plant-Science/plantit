from django.urls import path, include
from . import views

app_name = "user"
urlpatterns = [
    path('', views.user_landing, name="user_landing")
]
