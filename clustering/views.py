from turtle import st
from django.shortcuts import redirect, render
from .models import Customer
from .models import WeightRFM
from .resources import CustomerResources
from django.contrib import messages
from django.http.response import JsonResponse
from tablib import Dataset
from datetime import datetime
from clustering.kmeans import Kmeans
from clustering.minmaxnorm import MinMaxNorm
from clustering.silhouette_coefficient import SilhouetteCoefficient
from clustering.topsis import Topsis
from clustering.ahp import AhpWeight
from .utils import silhouette_bar, threedim_scatter_plot, silhouette_plot
from copy import deepcopy

# Create your views here.
def index(request):
    k_start = 2
    k_end = k_start
    transpose_dataNorm = False
    transpose_dataWeight =False
    cluster_visualization = False
    silhouette_visualization= False
    silhouette_line_plot = False
    centroids = False
    clusters = False
    matrixNorm = False
    matrixIdeal = False
    distanceAlter = False
    preferensi = False
    transpose_distanceAlter= False
    matrix_rankConsistency = False
    accuracy_rankConsistency = False
    clusters_member = False
    si_avg = False
    si_member_cluster = False
    centroids_type = False
    max_sc = False

    w = WeightRFM.objects.all().values()
    weight = {'r':w[0]['w_recency'], 'f':w[0]['w_frequency'], 'm':w[0]['w_monetary']}
    id_weight = w[0]['id']

    
    if request.FILES.get('myfile'):
        customer_resources = CustomerResources()
        dataset = Dataset()
        new_customer = request.FILES['myfile']

        if not new_customer.name.endswith('xlsx'):
            messages.info(request, 'wrong format')
            return render(request,'clustering/index.html')
        
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

    data_customers = Customer.objects.all().values()

    if request.POST.get('k_start') or request.POST.get('k_end'):
        if request.POST.get('k_start'):
            k_start = int(request.POST.get('k_start'))
        if request.POST.get('k_end'):
            k_end = int( request.POST.get('k_end'))
        
        data=[[],[],[]]
        for d in data_customers:
            data[0].append(d['recency'])
            data[1].append(d['frequency'])
            data[2].append(d['monetary'])
        
        #normalization
        data_norm = MinMaxNorm(data).calculate()

        #weighting
        data_weight = data_norm.copy()
        for i in range(len(weight)):
            data_weight[i] = list(map(lambda x : x * list(weight.values())[i], data_weight[i]))

        #kmeans
        max_sc = -1
        centroids = []
        clusters = []
        score_si = []
        cluster_visualization=[]
        silhouette_visualization=[]
        clusters_member = []
        si_avg  = []
        si_member_cluster = []
        for i in range(k_start,k_end+1):
            km = Kmeans(data = data_weight, k=i, max_iter=30).calculate()
            sc = SilhouetteCoefficient(km['clusters'], data_weight)
            scatter = threedim_scatter_plot(data_param=data_weight, labels=km['clusters'])
            cluster_visualization.append(scatter)
            silhoutte = silhouette_bar(score_si=sc.score_si, labels=km['clusters'])
            silhouette_visualization.append(silhoutte)
            temp_si_avg = [sc.avg_score, checkSilhouetteStructure(sc.avg_score)]
            si_avg.append(temp_si_avg)
            
            member = []
            si_cluster = []
            for j in range(i):
                iter=0
                si_status = {}
                no_stucture = 0
                weak_stucture = 0
                medium_stucture = 0
                strong_stucture = 0
                for index, data in enumerate(km['clusters']):
                    if j == data: 
                        iter+=1
                        if checkSilhouetteStructure(sc.score_si[index])=='No Structure':
                            no_stucture+=1
                        elif checkSilhouetteStructure(sc.score_si[index])=='Weak Structure':
                            weak_stucture+=1
                        elif checkSilhouetteStructure(sc.score_si[index])=='Medium Structure':
                            medium_stucture+=1
                        elif checkSilhouetteStructure(sc.score_si[index])=='Strong Structure':
                             strong_stucture+=1

                member.append(iter)
                si_status['strong_structure'] = strong_stucture
                si_status['medium_structure'] = medium_stucture
                si_status['weak_structure'] = weak_stucture
                si_status['no_structure'] = no_stucture
                si_cluster.append(si_status)
                

            clusters_member.append(member)
            si_member_cluster.append(si_cluster)

            if sc.avg_score > max_sc:
                max_sc = sc.avg_score
                score_si = sc.score_si
                centroids = km['centroids']
                clusters = km['clusters']
            print('Silhouette Coefficient jumlah k cluster '+str(i)+ ' : ' + str(sc.avg_score))

        # silhouette plot 
        silhouette_line_plot = silhouette_plot(x=[i+2 for i in range(len(si_avg))], y=[round(data[0],3) for data in si_avg])

        # topsis
        label_topsis = ['r','f','m']
        data={}
        for j in range(len(centroids[0])):
            temp=[]
            for i in range(len(centroids)):
                temp.append(centroids[i][j])
            data[label_topsis[j]] = temp

        
        benefit = ['f', 'm']
        cost = ['r']
        alternative_label = ['Cluster '+str(i+1) for i in range(len(centroids))]
        c = Topsis(data=data, benefit=benefit, cost=cost,alternative=alternative_label)
        top_pref = c.top_pref
        low_pref = c.low_pref
        matrixNorm = list(map(list, zip(*[data for data in c.matrixNorm.values()])))
        matrixIdeal = c.matrixIdeal
        distanceAlter = dict(c.distanceAlter)
        preferensi = c.result


        print('Result :')
        print(c.result)

        # Rank Consistency
        print('Rank Consistency :')
        data_uji = {}
        consitency = []
        matrix_rankConsistency=[]
        print(data)
        for i in range(len(centroids)):
            data_uji = data_uji.clear()
            data_uji = deepcopy(data)
            alternative_test = []
            for k, v in data.items():            
                data_uji[k].append(v[i])
            
            alternative_test = ['Cluster '+str(i+1) for i in range(len(centroids))]
            alternative_test.append('Alternatif Cluster '+str(i+1))
                   
            c = Topsis(data=data_uji, benefit=benefit, cost=cost, alternative=alternative_test)        
            print('Add alternatif ' + str(i))
            print(data_uji)
            print(c.result)
            matrix_rankConsistency.append(c.result)

            if top_pref == c.top_pref and low_pref == c.low_pref:
                consitency.append(1)
            else:
                consitency.append(0)
        print('Akurasi Rank Consistency : '+ str(sum(consitency)/len(consitency)*100)+'%')
        print(consitency)
        accuracy_rankConsistency = sum(consitency)/len(consitency)*100
        transpose_dataNorm = list(map(list, zip(*data_norm)))
        transpose_dataWeight = list(map(list, zip(*data_weight)))
        transpose_distanceAlter = list(map(list, zip(*[data for data in distanceAlter.values()])))

        centroids_type = []
        for data in centroids:
            type_r = checkTypeRFM('R', data[0], data_weight[0])
            type_f = checkTypeRFM('F', data[1], data_weight[1])
            type_m = checkTypeRFM('M', data[2], data_weight[2])
            centroids_type.append(dict({'r':data[0], 'f':data[1], 'm':data[2], 'type':type_r+type_f+type_m, 'strategy':type_f+type_m}))

    print(centroids_type)
    context ={
        'title':'Clustering',
        'customer':data_customers,
        'weight':weight,
        'data_norm' : transpose_dataNorm,
        'data_weight':transpose_dataWeight,
        'cluster_visualization' : cluster_visualization,
        'silhouette_visualization' :  silhouette_visualization,
        'silhouette_plot' :  silhouette_line_plot,
        'si_avg' : si_avg,
        'centroids' : centroids,
        'clusters' : clusters,
        'matrixNorm' : matrixNorm,
        'matrixIdeal': matrixIdeal,
        'distanceAlter': transpose_distanceAlter,
        'preferensi': preferensi,
        'matrix_rankConsistency': matrix_rankConsistency,
        'accuracy_rankConsistency' : accuracy_rankConsistency,
        'clusters_member' : clusters_member,
        'si_member_cluster' : si_member_cluster,
        'centroids_type':centroids_type,
        'id_weight': id_weight,
        'max_sc': [max_sc, checkSilhouetteStructure(max_sc)]
        
    }
    
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

def calculateahp(request):
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
            print('ini calculate ahp')
            print(weight)
            db_weight = WeightRFM.objects.get(id = request.POST.get('id_weight'))
            print(db_weight)
            db_weight.w_recency = weight['r']
            db_weight.w_frequency = weight['f']
            db_weight.w_monetary = weight['m']
            db_weight.score_input = str(ahp.comparison_matrix)
            db_weight.save()
            messages.info(request, 'success')
        else:
            messages.info(request, 'Please re-submit, because consintency ration more than 0.1')
    return redirect('clustering:index')

def recency(last_active_date, analysis_date):
    lastdate = datetime.fromisoformat(last_active_date).strftime("%Y-%m-%d")
    currentdate = datetime.fromisoformat(analysis_date).strftime("%Y-%m-%d")
    recency = datetime.strptime(currentdate,"%Y-%m-%d") - datetime.strptime(lastdate,"%Y-%m-%d")
    return recency.days

def checkTypeRFM(attribute, point_centroid, data_compare):
    if attribute == 'R':
        return 'R↑' if point_centroid > sum(data_compare)/len(data_compare) else 'R↓'
    elif attribute == 'F':
        return 'F↑' if point_centroid > sum(data_compare)/len(data_compare) else 'F↓'
    elif attribute == 'M':
        return 'M↑' if point_centroid > sum(data_compare)/len(data_compare) else 'M↓'
    else:
        return 'Wrong'

def checkStrategyRFM(type_rfm):
    if type_rfm == 'F↑M↑':
        return {
            'name' : 'Enforced Strategy (F↑ M↑)',
            'strategy' : [
                'Menjaga komunikasi dengan pelanggan.',
                'Menjaga interaktif jangka panjang.',
                'Merancang program loyalitas pelanggan.',
                'Mengerti kebutuhan dan kebiasaan pelanggan.'
            ],

            'saran' : [
                'Mengirim informasi promosi melalui telepon, fax dan email.',
                'Memberikan diskon pada acara tertentu.',
                'Melakukan wawancara dengan pelanggan mengenai penawaran produk melalui telepon.'
            ]
        }
    
    elif type_rfm == 'F↑M↓':
        return {
            'name' : 'Offensive Strategy (F↑ M↓)',
            'strategy' : [
               'Mempertahankan loyalitas pelanggan dengan kegiatan up-selling dan cross-selling',
               'Mempertahankan loyalitas dengan pelanggan.',
               'Mengembangkan kegiatan promosi untuk meningkatkan frekuensi',
               'Menarik minat pelanggan dengan produk atau layanan baru.'
            ],

            'saran' : [
                'Mempromosikan produk baru atau produk pelengkap.',
                'Meningkatkan pembelian pelanggan dengan menawarkan produk yang paling banyak dibeli.' 
            ]
        }
    
    elif type_rfm == 'F↓M↑':
        return  {
            'name' : 'Defensive Strategy (F↓ M↑)',
            'strategy' : [
                'Mengembangkan kegiatan promosi untuk meningkatkan frekuensi.',
                'Mengirim informasi produk/layanan secara berkala.'               
            ],

            'saran' : [
                'Merancang layanan purna jual.',
                'Menawarkan produk up-selling dengan harga khusus.'
            ]
        }

    elif type_rfm == 'F↓M↓':
        return  {
            'name' : 'Let-go Strategy (F↓ M↓)',
            'strategy' : [
               'Tidak ada keharusan perusahaan untuk memperhatikan segmen ini.',
               'Memilih produk dengan fokus utama yang dibutuhkan pelanggan.',
            ],

            'saran' : [
                'Memisahkan pelanggan baru dan pelanggan lama.',
                'Melakukan komunikasi hanya dengan pelanggan baru.'
            ]
        }
    else:
        return'kosong'

def checkSilhouetteStructure(si):
    if si <=0.25:
        return 'No Structure'
    elif si > 0.25 and si <=0.5:
        return 'Weak Structure'
    elif si > 0.5 and si <=0.7:
        return 'Medium Structure'
    elif si > 0.7 and si <=1:
        return 'Strong Structure'
    else:
        return ''

def getstrategy(request):
    data = checkStrategyRFM(request.GET.get('code_strategy'))
    data = {
        'data':data
    }
    return JsonResponse(data)   
