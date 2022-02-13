from django.urls import path
from clustering import views

urlpatterns = [
    path('', views.clustering_index, name="clustering_index"),
    path('calculate-ahp/', views.calculateahp, name="calculate-ahp"),
    path('get-startegy/', views.getstrategy, name="get-strategy"),
    #Dashboard
    path('dashboard/', views.dashboard, name="dashboard"),
    #Management Data
    path('managementdata/', views.managementdata, name="managementdata"),
    path('managementdata/update-cluster', views.update_cluster, name="update-cluster"),
    #Weight Model
    path('weightmodel/', views.weightmodel, name="weightmodel"),
    #RFM Model
    path('rfm/', views.rfm, name="rfm"),
    #LRFM Model
    path('lrfm/', views.lrfm, name="lrfm"),
    #Logout
    path('logout/', views.logout, name="logout")
]