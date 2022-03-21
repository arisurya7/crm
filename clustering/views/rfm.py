from django.shortcuts import redirect, render
from clustering.models import Customer, WeightRFM
from clustering.resources import CustomerResources, OrderResources
from django.contrib import messages
from tablib import Dataset
from datetime import date
from clustering.algorithm.kmeans import Kmeans
from clustering.algorithm.minmaxnorm import MinMaxNorm
from clustering.algorithm.silhouette_coefficient import SilhouetteCoefficient
from clustering.algorithm.topsis import Topsis
from clustering.utils import silhouette_bar, threedim_scatter_plot, silhouette_plot
from copy import deepcopy
from .checkmodel import checkTypeModel, checkSilhouetteStructure


def rfm(request):
    if request.session.has_key("user"):
        currentuser = request.session['user']
        context = {
            'title' : 'Model RFM',
            'isRfm' : True,
        }
        
        if request.POST.get('k_start') or request.POST.get('k_end'):
            if request.POST.get('k_start'):
                k_start = int(request.POST.get('k_start'))
            if request.POST.get('k_end'):
                k_end = int( request.POST.get('k_end'))
            
            data_customers = Customer.objects.filter(id_company = currentuser['id_company']).values()
            data=[[],[],[]]
            current_date = date(2022,1,1)
            for d in data_customers:
                # analysis_date = d['last_active']
                data[0].append(abs(d['last_active']-current_date).days)
                data[1].append(d['orders'])
                data[2].append(d['total_spend'])
            
            #data rfm
            data_rfm = list(map(list, zip(*data)))
            #normalization
            data_norm = MinMaxNorm(data).calculate()

            #weighting
            w = WeightRFM.objects.filter(id_company = currentuser['id_company']).values()
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
                    best_scatter = scatter
                    best_silhouette_bar = silhoutte
                    best_count_cluster = member
                    best_count_silhouette = si_cluster
                print('Silhouette Coefficient jumlah k cluster '+str(i)+ ' : ' + str(sc.avg_score))

            # silhouette plot 
            silhouette_line_plot = silhouette_plot(x=[k_start+i for i in range(len(si_avg))], y=[round(data[0],3) for data in si_avg])

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
            matrixNorm = list(map(list, zip(*[data for data in c.matrixNormalization().values()])))
            matrixIdeal = c.matrixIdealSolution()
            distanceAlter = dict(c.distanceAlternative())
            preferensi = c.preferensi()


            print('Result :')
            print(c.preferensi())

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
                print(c.preferensi())
                matrix_rankConsistency.append(c.preferensi())

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

            actual_cluster_member = []
            actual_cluster = []
            for i in range(max(clusters)+1):
                actual_cluster_member.append([])
                r_temp = []
                f_temp = []
                m_temp = []
                for j in range(len(clusters)):
                    row_data = {'name':'','email':'','r':0, 'f':0, 'm':0, 'cluster':i+1}
                    if i == clusters[j]:
                        row_data['name'] = data_customers[j]['name']
                        row_data['email'] = data_customers[j]['email']
                        row_data['r'] = data_rfm[j][0]
                        row_data['f'] = data_rfm[j][1]
                        row_data['m'] = data_rfm[j][2]
                        actual_cluster_member[i].append(row_data)
                        r_temp.append(data_rfm[j][0])
                        f_temp.append(data_rfm[j][1])
                        m_temp.append(data_rfm[j][2])
                        row_data = {'name':'','email':'','r':0, 'f':0, 'm':0, 'cluster':i+1}
                actual_cluster.append({'cluster': 'Cluster '+str(i+1), 'r':sum(r_temp)/len(r_temp), 'f':sum(f_temp)/len(f_temp), 'm':sum(m_temp)/len(m_temp)})
            
            id_customers = [ data['id_customer'] for data in data_customers]

            context['k_start'] = k_start
            context['data_rfm'] = data_rfm
            context['data_norm'] = transpose_dataNorm
            context['data_weight']=transpose_dataWeight
            context['cluster_visualization'] = cluster_visualization
            context['silhouette_visualization'] =  silhouette_visualization
            context['silhouette_plot'] =  silhouette_line_plot
            context['si_avg'] = si_avg
            context['centroids'] = centroids
            context['clusters'] = [list(pair) for pair in zip(id_customers, clusters)]
            context['matrixNorm'] = matrixNorm
            context['matrixIdeal']= matrixIdeal
            context['distanceAlter']= transpose_distanceAlter
            context['preferensi']= preferensi
            context['matrix_rankConsistency']= matrix_rankConsistency
            context['accuracy_rankConsistency'] = accuracy_rankConsistency
            context['clusters_member'] = clusters_member
            context['si_member_cluster'] = si_member_cluster
            context['centroids_type']=centroids_type
            context['max_sc']=[max_sc, checkSilhouetteStructure(max_sc)]
            context['actual_cluster'] = actual_cluster
            context['actual_cluster_member']= actual_cluster_member
            context['best_scatter']= best_scatter
            context['best_silhouette_bar']= best_silhouette_bar
            context['best_count_cluster']= best_count_cluster
            context['best_count_silhouette']= best_count_silhouette

        return render(request, 'clustering/rfm/index.html', context)
    else:
        return redirect('login')

