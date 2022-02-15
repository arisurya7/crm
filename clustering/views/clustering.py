import string
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
from .checkmodel import checkTypeModel, checkSilhouetteStructure
from copy import deepcopy


def clustering_index(request):
    
    context ={
        'title':'Clustering',        
    }
    
    return render(request,'clustering/index.html',context)

def general_rfm(request):
    request.session['weight_rfm'] = WeightRFM.objects.filter(id = 1).values()[0 ]
    context = {
        'weight_rfm' : request.session['weight_rfm'] if request.session.has_key('weight_rfm') else False
    }

    if request.FILES.get('myfile'):
        customer_resources = CustomerResources()
        dataset = Dataset()
        new_customer = request.FILES['myfile']

        if not new_customer.name.endswith('xlsx'):
            messages.info(request, 'wrong format')
            return render(request,'clustering/general_rfm.html')
        
        imported_data = dataset.load(new_customer.read(), format='xlsx')
        data_customers = []
        for i,data in enumerate(imported_data):
            row_data = {'id':i+1, 'r':0, 'f':0, 'm':0}
            row_data = {'id':i+1, 'r':data[1], 'f':data[2], 'm':data[3]}
            data_customers.append(row_data)
        request.session['data_customers'] = data_customers
    
    if request.POST.get('score3'):
        data_input = {}
        data_input[request.POST.get('input1')] = int(request.POST.get('score1'))
        data_input[request.POST.get('input2')] = int(request.POST.get('score2'))
        data_input[request.POST.get('input3')] = int(request.POST.get('score3'))
        criteria = ['r','f','m']
        ahp = AhpWeight(data_input, criteria)
        if(ahp.consistency_ratio < 0.1):
            weight = ahp.final_weight
            request.session['weight_rfm']['w_recency'] = weight['r']
            request.session['weight_rfm']['w_frequency'] = weight['f']
            request.session['weight_rfm']['w_monetary'] = weight['m']
            request.session['weight_rfm']['score_input'] = str(ahp.comparison_matrix)
            messages.info(request, 'success')
        else:
            messages.info(request, 'Please re-submit, because consintency ration more than 0.1')


    if request.POST.get('k_start') or request.POST.get('k_end'):
        if request.POST.get('k_start'):
            k_start = int(request.POST.get('k_start'))
        if request.POST.get('k_end'):
            k_end = int( request.POST.get('k_end'))
        
        data_customers = request.session['data_customers']
        data=[[],[],[]]
        for d in data_customers:
            data[0].append(d['r'])
            data[1].append(d['f'])
            data[2].append(d['m'])
        
        #data rfm
        data_rfm = list(map(list, zip(*data)))

        #normalization
        data_norm = MinMaxNorm(data).calculate()

        #weighting
        w = request.session['weight_rfm']
        weight = {'r':w['w_recency'], 'f':w['w_frequency'], 'm':w['w_monetary']}
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

        actual_cluster_member = []
        actual_cluster = []
        for i in range(max(clusters)+1):
            actual_cluster_member.append([])
            r_temp = []
            f_temp = []
            m_temp = []
            for j in range(len(clusters)):
                row_data = {'r':0, 'f':0, 'm':0, 'cluster':i+1}
                if i == clusters[j]:
                    row_data['r'] = data_rfm[j][0]
                    row_data['f'] = data_rfm[j][1]
                    row_data['m'] = data_rfm[j][2]
                    actual_cluster_member[i].append(row_data)
                    r_temp.append(data_rfm[j][0])
                    f_temp.append(data_rfm[j][1])
                    m_temp.append(data_rfm[j][2])
                    row_data = {'r':0, 'f':0, 'm':0, 'cluster':i+1}
            actual_cluster.append({'cluster': 'Cluster '+str(i+1), 'r':sum(r_temp)/len(r_temp), 'f':sum(f_temp)/len(f_temp), 'm':sum(m_temp)/len(m_temp)})
        
        id_customers = [ data['id'] for data in data_customers]

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


    context['data_customers'] = request.session['data_customers'] if request.session.has_key("data_customers") else False

    return render(request,'clustering/general_rfm.html', context)

def clear_general_rfm(request):
    try:
        del request.session['data_customers']
        del request.session['weight_rfm']
    except:
        return redirect('clustering:general-rfm')
    return redirect('clustering:general-rfm')

def general_lrfm(request):
    request.session['weight_lrfm'] = WeightLRFM.objects.filter(id = 1).values()[0 ]
    context = {
        'weight_lrfm' : request.session['weight_lrfm'] if request.session.has_key('weight_lrfm') else False
    }

    if request.FILES.get('myfile'):
        customer_resources = CustomerResources()
        dataset = Dataset()
        new_customer = request.FILES['myfile']

        if not new_customer.name.endswith('xlsx'):
            messages.info(request, 'wrong format')
            return render(request,'clustering/general_rfm.html')
        
        imported_data = dataset.load(new_customer.read(), format='xlsx')
        data_customers_lrfm = []
        for i,data in enumerate(imported_data):
            row_data = {'id':i+1, 'l':0, 'r':0, 'f':0, 'm':0}
            row_data = {'id':i+1, 'l':data[1], 'r':data[2], 'f':data[3], 'm':data[4]}
            data_customers_lrfm.append(row_data)
        request.session['data_customers_lrfm'] = data_customers_lrfm
    
    if request.POST.get('score6'):
        data_input = {}
        data_input[request.POST.get('input1')] = int(request.POST.get('score1'))
        data_input[request.POST.get('input2')] = int(request.POST.get('score2'))
        data_input[request.POST.get('input3')] = int(request.POST.get('score3'))
        data_input[request.POST.get('input4')] = int(request.POST.get('score4'))
        data_input[request.POST.get('input5')] = int(request.POST.get('score5'))
        data_input[request.POST.get('input6')] = int(request.POST.get('score6'))
        criteria = ['l','r','f','m']

        ahp = AhpWeight(data_input, criteria)
        if(ahp.consistency_ratio < 0.1):
            weight = ahp.final_weight
            request.session['weight_lrfm']['w_length'] = weight['l']
            request.session['weight_lrfm']['w_recency'] = weight['r']
            request.session['weight_lrfm']['w_frequency'] = weight['f']
            request.session['weight_lrfm']['w_monetary'] = weight['m']
            request.session['weight_lrfm']['score_input'] = str(ahp.comparison_matrix)
            messages.info(request, 'success')
        else:
            messages.info(request, 'Please re-submit, because consintency ration more than 0.1')

    if request.POST.get('k_start') or request.POST.get('k_end'):
        if request.POST.get('k_start'):
            k_start = int(request.POST.get('k_start'))
        if request.POST.get('k_end'):
            k_end = int( request.POST.get('k_end'))
        
        data_customers_lrfm = request.session['data_customers_lrfm']
        data=[[],[],[],[]]
        for d in data_customers_lrfm:
            data[0].append(d['l'])
            data[1].append(d['r'])
            data[2].append(d['f'])
            data[3].append(d['m'])
        
        #data lrfm
        data_lrfm = list(map(list, zip(*data)))

        #normalization
        data_norm = MinMaxNorm(data).calculate()

        #weighting
        w = request.session['weight_lrfm']
        weight = {'l':w['w_length'],'r':w['w_recency'], 'f':w['w_frequency'], 'm':w['w_monetary']}
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
        label_topsis = ['l','r','f','m']
        data={}
        for j in range(len(centroids[0])):
            temp=[]
            for i in range(len(centroids)):
                temp.append(centroids[i][j])
            data[label_topsis[j]] = temp

        
        benefit = ['f', 'm']
        cost = ['l','r']
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
            type_l = checkTypeModel('L', data[0], data_weight[0])
            type_r = checkTypeModel('R', data[1], data_weight[1])
            type_f = checkTypeModel('F', data[2], data_weight[2])
            type_m = checkTypeModel('M', data[3], data_weight[3])
            centroids_type.append(dict({'l':data[0],'r':data[1], 'f':data[2], 'm':data[3], 'type':type_l+type_r+type_f+type_m, 'strategy':type_f+type_m}))

        actual_cluster_member = []
        actual_cluster = []
        for i in range(max(clusters)+1):
            actual_cluster_member.append([])
            l_temp = []
            r_temp = []
            f_temp = []
            m_temp = []
            for j in range(len(clusters)):
                row_data = {'id':j+1, 'l':0,'r':0, 'f':0, 'm':0, 'cluster':i+1}
                if i == clusters[j]:
                    row_data['l'] = data_lrfm[j][0]
                    row_data['r'] = data_lrfm[j][1]
                    row_data['f'] = data_lrfm[j][2]
                    row_data['m'] = data_lrfm[j][3]
                    actual_cluster_member[i].append(row_data)
                    l_temp.append(data_lrfm[j][0])
                    r_temp.append(data_lrfm[j][1])
                    f_temp.append(data_lrfm[j][2])
                    m_temp.append(data_lrfm[j][3])
                    row_data = {'id':i+1,'l':0,'r':0, 'f':0, 'm':0, 'cluster':i+1}
            actual_cluster.append({'cluster': 'Cluster '+str(i+1), 'l':sum(l_temp)/len(l_temp), 'r':sum(r_temp)/len(r_temp), 'f':sum(f_temp)/len(f_temp), 'm':sum(m_temp)/len(m_temp)})
        
        id_customers = [ data['id'] for data in data_customers_lrfm]

        context['k_start'] = k_start
        context['data_lrfm'] = data_lrfm
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
        
    context['data_customers_lrfm'] = request.session['data_customers_lrfm'] if request.session.has_key("data_customers_lrfm") else False
    return render(request,'clustering/general_lrfm.html', context)

def clear_general_lrfm(request):
    try:
        del request.session['data_customers_lrfm']
        del request.session['weight_lrfm']
    except:
        return redirect('clustering:general-lrfm')
    return redirect('clustering:general-lrfm')