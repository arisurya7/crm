from turtle import st
from django.shortcuts import render
from .models import Customer
from .resources import CustomerResources
from django.contrib import messages
from tablib import Dataset
from datetime import datetime
from clustering.kmeans import Kmeans
from clustering.minmaxnorm import MinMaxNorm
from clustering.silhouette_coefficient import SilhouetteCoefficient
from clustering.topsis import Topsis
from clustering.ahp import AhpWeight
from .utils import silhouette_bar, threedim_scatter_plot
from copy import deepcopy

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
    max_sc = -1
    centroids = []
    clusters = []
    score_si = []
    for i in range(2,7):
        km = Kmeans(data = data_norm, k=i, max_iter=30).calculate()
        sc = SilhouetteCoefficient(km['clusters'], data_norm)
        if sc.avg_score > max_sc:
            max_sc = sc.avg_score
            score_si = sc.score_si
            centroids = km['centroids']
            clusters = km['clusters']
        print('Silhouette Coefficient jumlah k cluster '+str(i)+ ' : ' + str(sc.avg_score))

    # topsis
    label_topsis = ['r','f','m']
    data={}
    for j in range(len(centroids[0])):
        temp=[]
        for i in range(len(centroids)):
            temp.append(centroids[i][j])
        data[label_topsis[j]] = temp

    weight = [0.097, 0.3446, 0.5583]
    benefit = ['f', 'm']
    cost = ['r']

    c = Topsis(data, weight, benefit, cost)
    top_pref = c.top_pref
    low_pref = c.low_pref
    print('Result :')
    print(c.result)

    # Rank Consistency
    print('Rank Consistency :')
    data_uji = {}
    consitency = []
    print(data)
    for i in range(len(data[label_topsis[0]])):
        data_uji = data_uji.clear()
        data_uji = deepcopy(data)
        for k, v in data.items():            
            data_uji[k].append(v[i])
            
        c = Topsis(data_uji, weight, benefit, cost)        
        print('Add alternatif ' + str(i))
        print(c.result)

        if top_pref == c.top_pref and low_pref == c.low_pref:
            consitency.append(1)
        else:
            consitency.append(0)
    print('Akurasi Rank Consistency : '+ str(sum(consitency)/len(consitency)*100)+'%')

    chart = threedim_scatter_plot(data_param=data_norm, labels=clusters)
    context['chart'] = chart
    context['si_chart'] = silhouette_bar(score_si=score_si, labels=clusters)

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

def ahp(request):
    weight = {'r':0.097, 'f':0.3446, 'm':0.5583}
    data_input = {}
    if request.POST:
        data_input[request.POST.get('input1')] = int(request.POST.get('score1'))
        data_input[request.POST.get('input2')] = int(request.POST.get('score2'))
        data_input[request.POST.get('input3')] = int(request.POST.get('score3'))

    criteria = ['r','f','m']

    if(len(data_input)>0):
        ahp = AhpWeight(data_input, criteria)
        if(ahp.consistency_ratio < 0.1):
            weight = ahp.final_weight
        else:
            messages.info(request, 'Please re-submit, because consintency ration more than 0.1')

    context = {
        'title' : 'AHP',
        'weight':weight
    }
    return render(request, 'clustering/ahp.html', context)

def recency(last_active_date, analysis_date):
    lastdate = datetime.fromisoformat(last_active_date).strftime("%Y-%m-%d")
    currentdate = datetime.fromisoformat(analysis_date).strftime("%Y-%m-%d")
    recency = datetime.strptime(currentdate,"%Y-%m-%d") - datetime.strptime(lastdate,"%Y-%m-%d")
    return recency.days



