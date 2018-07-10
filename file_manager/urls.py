from django.contrib import admin
from django.urls import path
from file_manager import views

app_name = "file_manager"
urlpatterns = [
    path('', views.filepicker, name='file_browser'),
    path('ajax/<command>/',views.FileBrowserView.as_view(),name='ajax')
]
