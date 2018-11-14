from django.urls import path, include
from collection import views

app_name = "collection"
urlpatterns = [
    path('',views.List.as_view(), name="list"),
    path('new/', views.New.as_view(), name="new"),
    path('<pk>/details/',views.Details.as_view(), name="details"),
    # path('<pk>/analyze/',views.Analyze.as_view(), name="analyze"),
    path('<pk>/edit/files',views.AddFiles.as_view(), name="edit_files"),
    path('<pk>/edit/details',views.EditDetails.as_view(),name="edit_details")
]
