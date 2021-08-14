from django.urls import path

from . import views

urlpatterns = [
    path(r'sharing/', views.sharing),
    path(r'shared/', views.shared),
    path(r'share/', views.share),
    path(r'unshare/', views.unshare),
    path(r'create/', views.create),
    path(r'bind/', views.bind),
    path(r'unbind/', views.unbind)
]