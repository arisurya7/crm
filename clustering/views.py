from django.shortcuts import render
from .models import Customer
from .resources import CustomerResources
from django.contrib import messages
from tablib import Dataset
from django.http import HttpResponse
from math import sqrt
from random import sample
from datetime import datetime
from clustering.kmeans import Kmeans
from clustering.minmaxnorm import MinMaxNorm

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

def kmeans(request):
    context = {
        'title': 'KMeans'
    }
    
    alldata = Customer.objects.all().values()
    data=[[],[],[]]
    for d in alldata:
        data[0].append(d['recency'])
        data[1].append(d['frequency'])
        data[2].append(d['monetary'])

    # r = recency('2022-01-09T12:20:42','2022-01-11T12:20:42')
    # print(r)

    #min-max normalisasi
    data_norm = MinMaxNorm(data).calculate()

    #kmeans
    km = Kmeans(data = data_norm, k=3, max_iter=3).calculate()
    print(km['data_distance'])
    print(km['clusters'])
    print(km['centroids'])

    return render(request,'clustering/kmeans.html', context)


def recency(last_active_date, analysis_date):
    lastdate = datetime.fromisoformat(last_active_date).strftime("%Y-%m-%d")
    currentdate = datetime.fromisoformat(analysis_date).strftime("%Y-%m-%d")
    recency = datetime.strptime(currentdate,"%Y-%m-%d") - datetime.strptime(lastdate,"%Y-%m-%d")
    return recency.days



