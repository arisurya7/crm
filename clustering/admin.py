from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from matplotlib.pyplot import cla
from .models import Customer
from .models import Order
from .models import WeightRFM
from .models import WeightLRFM
from .resources import *

@admin.register(Customer)
class CustomerAdmin(ImportExportModelAdmin):
    resource_class  =   CustomerResources
    list_display = ('id_customer', 'name', 'email', 'last_active', 'orders', 'total_spend','aov','country', 'city', 'region')

@admin.register(Order)
class OrderAdmin(ImportExportModelAdmin):
    resource_class  =   OrderResources
    list_display = ('id_order', 'name', 'date', 'status', 'total')

# admin.site.register(WeightRFM)
@admin.register(WeightRFM)
class WeightRFMAdmin(admin.ModelAdmin):
    list_display = ('id','w_recency', 'w_frequency', 'w_monetary', 'score_input')

@admin.register(WeightLRFM)
class WeightLRFMAdmin(admin.ModelAdmin):
    list_display = ('id','w_length','w_recency', 'w_frequency', 'w_monetary', 'score_input')