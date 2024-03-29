import string
import csv
from django.shortcuts import redirect, render
from django.http.response import JsonResponse, HttpResponse
from clustering.models import Customer, Order
from clustering.resources import CustomerResources, OrderResources
from django.contrib import messages
from tablib import Dataset
from datetime import datetime
from datetime import date

def managementdata(request):
    if request.session.has_key("user"):
        current_user = request.session['user']

        if request.FILES.get('myfile'):
            customer_resources = CustomerResources()
            dataset = Dataset()
            new_customer = request.FILES['myfile']

            if not new_customer.name.endswith('xlsx'):
                messages.info(request, 'wrong format')
                return render(request,'clustering/managementdata/index.html')
            
            imported_data = dataset.load(new_customer.read(), format='xlsx')
            for data in imported_data:
                if(isinstance(data[2], datetime)):
                    last_active = data[2]
                elif len(data[2])>10:
                    # last_active = data[2][:10]
                    last_active = datetime.strptime(data[2], "%Y-%m-%dT%H:%M:%S")
                else:
                    last_active = data[2]

                value = Customer(
                    data[0],
                    current_user['id_company'],
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
                if(isinstance(data[3], datetime)):
                    date = data[3]
                else:
                    if len(data[3])>10:
                        date = data[3][:10]
                    else:
                        date = data[3]
                        
                value = Order(
                    data[0],
                    current_user['id_company'],
                    data[1],
                    data[2],
                    date,
                    data[4],
                    data[5],
                )

                value.save()

        customers = Customer.objects.all().values()
        orders = Order.objects.all().values()
        context = {
            'title' : 'Management Data',
            'isManagementData' : True,
            'customers': customers,
            'orders':orders,
            'role':current_user['role']
        }
        return render(request, 'clustering/managementdata/index.html', context)

    else:
        return redirect('login')

def export_data_customer(request):
    if request.session.has_key("user"):
        currentuser = request.session['user']
        data_customers = Customer.objects.filter(id_company = currentuser['id_company']).values()
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="data_customer.csv"'},
            )

        writer = csv.writer(response)
        writer.writerow(['id_customer', 'name', 'last_active', 'email', 'orders', 'total_spend', 'aov', 'country', 'city', 'region', 'cluster'])
        
        for d in data_customers:
             writer.writerow([d['id_customer'], d['name'], d['last_active'], d['email'], d['orders'], d['total_spend'], d['aov'], d['country'], d['city'], d['region'], d['cluster']])
        return response
    
    else:
        return redirect('login')

def export_data_order(request):
    if request.session.has_key("user"):
        currentuser = request.session['user']
        data_orders = Order.objects.filter(id_company = currentuser['id_company']).values()
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="data_order.csv"'},
            )

        writer = csv.writer(response)
        writer.writerow(['id_order','id_customer', 'name', 'date', 'status', 'total'])
        
        for d in data_orders:
             writer.writerow([d['id_order'], d['id_customer'], d['name'], d['date'], d['status'], d['total']])
        return response
    
    else:
        return redirect('login')
    

    

def update_cluster(request):
    if request.session.has_key("user"):
        current_user = request.session['user']
        if request.POST.get('clusters[]'):
            list_clusters = request.POST.getlist('clusters[]')
            for data in list_clusters:
                data = list(data.split(","))
                Customer.objects.filter(id_customer = int(data[0]), id_company = current_user['id_company']).update(cluster = (int(data[1])+1))
            return JsonResponse({'status':'Success'})
    else:
        return redirect('login')

def delete_all_customer(request):
    if request.session.has_key("user"):
        current_user = request.session["user"]
        if request.POST.get('delete_all'):
            Customer.objects.filter(id_company=current_user['id_company']).delete()
            return redirect('clustering:managementdata')
    else:
        return redirect('login')

def delete_all_order(request):
    if request.session.has_key("user"):
        current_user = request.session["user"]
        if request.POST.get('delete_all'):
            Order.objects.filter(id_company=current_user['id_company']).delete()
            return redirect('clustering:managementdata')
    else:
        return redirect('login')