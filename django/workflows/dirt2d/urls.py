from django.urls import path
from workflows.dirt2d import views

app_name = "dirt2d"
urlpatterns = [
    # path('choose',views.Choose.as_view(),name="choose"),
    path('submit/<pk>/',views.Analyze.as_view(),name="analyze"),
    path('submit/<pk>/segment/',views.segment_image,name="segment")
]
