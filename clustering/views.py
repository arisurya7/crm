from django.shortcuts import render
from .models import Customer
from .resources import CustomerResources
from django.contrib import messages
from tablib import Dataset
from django.http import HttpResponse

# Create your views here.
def index(request):
    context ={
        'title':'Clustering',
        'customer':[]
    }

    if request.method == 'POST':
        customer_resources = CustomerResources()
        dataset = Dataset()
        new_customer = request.FILES['myfile']

        if not new_customer.name.endswith('xlsx'):
            messages.info(request, 'wrong format')
            return render(request,'clustering/index.html',context)
        
        imported_data = dataset.load(new_customer.read(), format='xlsx')
        for data in imported_data:
            value = Customer(
                data[0],
                data[1],
                data[2],
                data[3],
                data[4],
                data[5]
            )

            value.save()
    
    context['customer'] = Customer.objects.all().values()
    
    return render(request,'clustering/index.html',context)