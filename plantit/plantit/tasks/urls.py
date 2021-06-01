from django.urls import path

from . import views

urlpatterns = [
    path(r'agent/', views.search_or_add_agent_task),
    path(r'agent/<name>/', views.get_or_delete_agent_task),
    path(r'agent/<name>/toggle/', views.toggle_agent_task),
    path(r'delayed/', views.search_or_add_delayed_task),
    path(r'delayed/<name>/', views.get_or_delete_delayed_task),
    path(r'delayed/<name>/toggle/', views.toggle_delayed_task),
    path(r'repeating/', views.search_or_add_repeating_task),
    path(r'repeating/<name>/', views.get_or_delete_repeating_task),
    path(r'repeating/<name>/toggle/', views.toggle_repeating_task),
]