import string
from turtle import st
from django.shortcuts import redirect, render
from clustering.models import Customer, Order, WeightLRFM, WeightRFM
from clustering.resources import CustomerResources, OrderResources
from django.contrib import messages
from django.http.response import JsonResponse
from tablib import Dataset
from datetime import datetime
from datetime import date
from clustering.algorithm.kmeans import Kmeans
from clustering.algorithm.minmaxnorm import MinMaxNorm
from clustering.algorithm.silhouette_coefficient import SilhouetteCoefficient
from clustering.algorithm.topsis import Topsis
from clustering.algorithm.ahp import AhpWeight
from clustering.utils import silhouette_bar, threedim_scatter_plot, silhouette_plot
from copy import deepcopy


def rfm(request):
    data_rfm = False
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
    
    if request.POST.get('k_start') or request.POST.get('k_end'):
        if request.POST.get('k_start'):
            k_start = int(request.POST.get('k_start'))
        if request.POST.get('k_end'):
            k_end = int( request.POST.get('k_end'))
        
        data_customers = Customer.objects.all().values()
        data=[[],[],[]]
        current_date = date(2021,4,1)
        for d in data_customers:
            analysis_date = d['last_active']
            data[0].append(recency(analysis_date, current_date))
            data[1].append(d['orders'])
            data[2].append(d['total_spend'])
        
        #data rfm
        data_rfm = list(map(list, zip(*data)))
        #normalization
        data_norm = MinMaxNorm(data).calculate()

        #weighting
        w = WeightRFM.objects.all().values()
        weight = {'r':w[0]['w_recency'], 'f':w[0]['w_frequency'], 'm':w[0]['w_monetary']}
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
            type_r = checkTypeModel('R', data[0], data_weight[0])
            type_f = checkTypeModel('F', data[1], data_weight[1])
            type_m = checkTypeModel('M', data[2], data_weight[2])
            centroids_type.append(dict({'r':data[0], 'f':data[1], 'm':data[2], 'type':type_r+type_f+type_m, 'strategy':type_f+type_m}))

    print(centroids_type)



    context = {
        'title' : 'Model RFM',
        'isRfm' : True,
        'data_rfm' : data_rfm,
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
        'max_sc': [max_sc, checkSilhouetteStructure(max_sc)]
    }
    return render(request, 'clustering/rfm/index.html', context)


def recency(last_active_date, analysis_date):
    #This is for string format date
    # lastdate = datetime.fromisoformat(last_active_date).strftime("%Y-%m-%d")
    # currentdate = datetime.fromisoformat(analysis_date).strftime("%Y-%m-%d")
    # recency = abs(datetime.strptime(currentdate,"%Y-%m-%d") - datetime.strptime(lastdate,"%Y-%m-%d"))
    #This is for datetime format
    recency = abs(last_active_date-analysis_date)
    return recency.days

def lrfm_length(length_date, last_active):
    length_lrfm = abs(last_active-length_date)
    return length_lrfm.days

def checkTypeModel(attribute, point_centroid, data_compare):
    if attribute == 'L':
        return 'L↑' if point_centroid > sum(data_compare)/len(data_compare) else 'L↓'
    elif attribute == 'R':
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