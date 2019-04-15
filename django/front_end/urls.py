from django.contrib import admin
from django.urls import path, include
from .src.plantit import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index),
    path('jobs/', include('front_end.src.job_manager.urls')),
    path('workflows/', include('front_end.src.workflows.urls')),
    path('collection/', include('front_end.src.collection.urls')),
    path('user/', include('front_end.src.user.urls'))
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
