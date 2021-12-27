from import_export import resources
from .models import Customer

class CustomerResources(resources.ModelResource):
    class meta:
        model = Customer