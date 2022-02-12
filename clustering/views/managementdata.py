import string
from turtle import st
from django.shortcuts import redirect, render
from clustering.models import Customer, Order
from clustering.resources import CustomerResources, OrderResources
from django.contrib import messages
from tablib import Dataset
from datetime import datetime
from datetime import date

def managementdata(request):
    if request.FILES.get('myfile'):
        customer_resources = CustomerResources()
        dataset = Dataset()
        new_customer = request.FILES['myfile']

        if not new_customer.name.endswith('xlsx'):
            messages.info(request, 'wrong format')
            return render(request,'clustering/managementdata/index.html')
        
        imported_data = dataset.load(new_customer.read(), format='xlsx')
        for data in imported_data:
            if len(data[2])>10:
                last_active = data[2][:10]
            else:
                last_active = data[2]

            value = Customer(
                data[0],
                data[1],
                last_active,
                data[3],
                data[4],
                data[5],
                data[6],
                data[7],
                data[8],
                data[9],
            )

            value.save()

    if request.FILES.get('myorders'):
        customer_resources = OrderResources
        dataset = Dataset()
        new_orders = request.FILES['myorders']

        if not new_orders.name.endswith('xlsx'):
            messages.info(request, 'wrong format')
            return render(request,'clustering/managementdata/index.html')
        
        imported_data = dataset.load(new_orders.read(), format='xlsx')
        for data in imported_data:
            if(isinstance(data[2], datetime)):
                date = data[2]
            else:
                if len(data[2])>10:
                    date = data[2][:10]
                else:
                    date = data[2]
                    
            value = Order(
                data[0],
                data[1],
                date,
                data[3],
                data[4],
            )

            value.save()
    
    customers = Customer.objects.all().values()
    orders = Order.objects.all().values()
    context = {
        'title' : 'Management Data',
        'isManagementData' : True,
        'customers': customers,
        'orders':orders,
    }
    return render(request, 'clustering/managementdata/index.html', context)
