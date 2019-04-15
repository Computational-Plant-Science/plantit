from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('files/', include('apis.file_manager.urls')),
    path('jobs/',include('apis.job_manager.urls')),
    path('collections/',include('apis.collection.urls'))
]
