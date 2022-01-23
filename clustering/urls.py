from django.urls import path
from clustering import views

urlpatterns = [
    path('', views.index, name="index"),
    path('kmeans/', views.kmeans, name="kmeans"),
    path('visualization/', views.visualization, name="visualization"),
    path('ahp/', views.ahp, name="ahp")
]