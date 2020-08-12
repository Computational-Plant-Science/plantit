from django.urls import path

from . import views

urlpatterns = [
    path(r'', views.list_all),
    path(r'<owner>/', views.list_by_owner),
    path(r'<owner>/<name>/', views.get_by_owner_and_name),
    # path(r'<owner>/<name>/delete/', views.delete_by_owner_and_name),
    path(r'create/', views.create),
    path(r'<owner>/<name>/list_metadata/', views.list_metadata),
    path(r'<owner>/<name>/update_description/', views.update_description),
    path(r'<owner>/<name>/update_metadata/', views.update_metadata),
    path(r'<owner>/<name>/list_files/', views.list_files),
    path(r'<owner>/<name>/upload_files/', views.upload_files),
    path(r'<owner>/<name>/download_files/', views.download_files),
    path(r'<owner>/<name>/delete_files/', views.delete_files),
]
