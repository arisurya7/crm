from django.urls import path
from clustering import views

urlpatterns = [
    path('', views.index, name="index")
]