from django.shortcuts import render
from .models import Customer
from .resources import CustomerResources
from django.contrib import messages
from tablib import Dataset
from datetime import datetime
from clustering.kmeans import Kmeans
from clustering.minmaxnorm import MinMaxNorm
from clustering.silhouette_coefficient import SilhouetteCoefficient
from .utils import threedim_scatter_plot

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
    for i in range(2,7):
        km = Kmeans(data = data_norm, k=i, max_iter=30).calculate()
        sc = SilhouetteCoefficient(km['clusters'], data_norm)
        print('Silhouette Coefficient jumlah k cluster '+str(i)+ ' : ' + str(sc.avg_score))

    return render(request,'clustering/kmeans.html', context)

def visualization(request):
    x = [0.2863605215247132, 0.7183205790430133, 0.8909072122814039, 0.23030682728548083, 0.21838894634244435, 0.9298784163965758, 0.8849141822400217, 0.727018197588752, 0.272918189925625, 0.27007304438783025]
    y = [0.7778846613395983, 0.4072157280537751, 0.2848026139707954, 0.8329557805984333, 0.8929790411597495, 1.196794707666691, 0.846590328824407, 0.1687301415359526, 0.526849263606065, 0.7490040516112245]
    z = [1.1421632616876678, 1.3009721208877132, 0.9134099752594813, 0.8540685230687318, 0.9635118968263423, 0.27435278684341147, 0.2743527868434114, 0.8638874795492136, 0.8645236853256344, 0.6028722551949356]
    chart = threedim_scatter_plot(x,y,z)
    context = {
        'title': 'Visualization',
        'chart' :chart
    }
    return render(request,'clustering/visualization.html',context)

def recency(last_active_date, analysis_date):
    lastdate = datetime.fromisoformat(last_active_date).strftime("%Y-%m-%d")
    currentdate = datetime.fromisoformat(analysis_date).strftime("%Y-%m-%d")
    recency = datetime.strptime(currentdate,"%Y-%m-%d") - datetime.strptime(lastdate,"%Y-%m-%d")
    return recency.days



