from django.urls import path, include

app_name = "workflows"
urlpatterns = [
    path('dirt2d/', include('workflows.dirt2d.urls'), name="dirt2d"),
]
