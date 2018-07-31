from django.urls import path
from workflows.dirt2d import views

app_name = "dirt2d"
urlpatterns = [
    path('',views.ListView.as_view()),
    path('collection/new/', views.New.as_view(), name="new"),
    path('collection/<pk>/images/',views.ImageView.as_view(), name="images"),
    path('collection/<pk>/details/',views.DetailView.as_view(), name="details"),
    path('collection/<pk>/analyze/',views.Analyze.as_view(), name="analyze"),
    path('collection/<pk>/edit/images',views.EditFiles.as_view(), name="edit_images"),
    path('collection/<pk>/edit/details',views.EditDetails.as_view(),name="edit_details")
]
