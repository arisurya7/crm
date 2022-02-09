from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from matplotlib.pyplot import cla
from .models import Customer
from .models import WeightRFM

@admin.register(Customer)
class CustomerAdmin(ImportExportModelAdmin):
    list_display = ('id_customer', 'name', 'email', 'recency', 'frequency', 'monetary')

# admin.site.register(WeightRFM)

@admin.register(WeightRFM)
class WeightRFMAdmin(admin.ModelAdmin):
    list_display = ('id','w_recency', 'w_frequency', 'w_monetary', 'score_input')