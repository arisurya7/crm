from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from matplotlib.pyplot import cla
from .models import Customer, Order,WeightRFM, WeightLRFM, Company, UserCompany
from .resources import *

@admin.register(Customer)
class CustomerAdmin(ImportExportModelAdmin):
    resource_class  =   CustomerResources
    list_display = ('id_customer','id_company', 'name', 'email', 'last_active', 'orders', 'total_spend','aov','country', 'city', 'region', 'cluster')

@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    resource_class  =   OrderResources
    list_display = ('id_order','id_company', 'name', 'date', 'status', 'total')

# admin.site.register(WeightRFM)
@admin.register(WeightRFM)
class WeightRFMAdmin(admin.ModelAdmin):
    list_display = ('id','id_company','w_recency', 'w_frequency', 'w_monetary', 'score_input')

@admin.register(WeightLRFM)
class WeightLRFMAdmin(admin.ModelAdmin):
    list_display = ('id','id_company','w_length','w_recency', 'w_frequency', 'w_monetary', 'score_input')

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id_company','name','telp', 'email', 'address')

@admin.register(UserCompany)
class UserCompanyAdmin(admin.ModelAdmin):
    list_display = ('id_user','id_company','name','email', 'username', 'password', 'verified', 'role')
      