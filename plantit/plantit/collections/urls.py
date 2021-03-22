from django.urls import path

from . import views

urlpatterns = [
    path(r'share/', views.share),
    path(r'unshare/', views.unshare),
    path(r'sharing/', views.sharing),
    path(r'shared/', views.shared),
    path(r'opened/', views.opened_session),
    path(r'open/', views.open_session),
    path(r'close/', views.close_session),
    path(r'thumbnail/', views.get_thumbnail),
    path(r'content/', views.get_text_content)
]