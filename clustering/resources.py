from import_export import resources
from .models import Customer
from .models import Order

class CustomerResources(resources.ModelResource):
    class meta:
        model = Customer
        # import_id_fields = ('id_customer',)
        # fields = ('id_customer', 'name', 'email', 'last_active', 'orders', 'total_spend','aov','country', 'city', 'region')

class OrderResources(resources.ModelResource):
    class meta:
        model = Order
        exclude = ('id',)