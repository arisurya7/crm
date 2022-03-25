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
    #Testing
    path('testing/', views.testing, name="testing"),
    path('testing-volumedata/', views.testing_volumedata, name="testing-volumedata"),
    #Rekomendasi
    path('rekomendasi/', views.rekomendasi, name="rekomendasi"),
    #Clear Rekomendasi
    path('clear-rekomendasi/', views.clear_rekomendasi, name="clear-rekomendasi"),
    #General RFM
    path('general-rfm', views.general_rfm, name = "general-rfm"),
    path('clear-general-rfm', views.clear_general_rfm, name = "clear-general-rfm"),
    #General LRFM
    path('general-lrfm', views.general_lrfm, name = "general-lrfm"),
    path('clear-general-lrfm', views.clear_general_lrfm, name = "clear-general-lrfm"),
    #Logout
    path('logout/', views.logout, name="logout")
]