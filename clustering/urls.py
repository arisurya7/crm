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
    path('managementdata/export-data-customer', views.export_data_customer, name="export-data-customer"),
    path('managementdata/export-data-order', views.export_data_order, name="export-data-order"),
    path('managementdata/update-cluster', views.update_cluster, name="update-cluster"),
    path('managementdata/delete-all-customer', views.delete_all_customer, name="delete-all-customer"),
    path('managementdata/delete-all-order', views.delete_all_order, name="delete-all-order"),
    #Weight Model
    path('weightmodel/', views.weightmodel, name="weightmodel"),
    #RFM Model
    path('rfm/', views.rfm, name="rfm"),
    #LRFM Model
    path('lrfm/', views.lrfm, name="lrfm"),
    #Testing
    path('testing/', views.testing, name="testing"),
    path('testing-volumedata/', views.testing_volumedata, name="testing-volumedata"),
    path('testing-validasitopsis/', views.testing_validasitopsis, name="testing-validasitopsis"),
    path('testing-rankconsistency/', views.testing_rankconsistency, name="testing-rankconsistency"),
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