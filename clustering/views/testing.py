from django.shortcuts import render, redirect
from datetime import date,datetime
from clustering.algorithm.kmeans import Kmeans
from clustering.algorithm.minmaxnorm import MinMaxNorm
from clustering.algorithm.silhouette_coefficient import SilhouetteCoefficient
from clustering.algorithm.topsis import Topsis
from clustering.models import Customer, Order
from clustering.utils import testing_sc_bar, grouped_two_bar
from copy import deepcopy
import numpy as np


def testing(request):
    if request.session.has_key("user"):
        currentuser = request.session['user']
        context = {
            'title' : 'Skenario 2',
            'isTesting' : True
        }

        if request.POST.get('k_start') or request.POST.get('k_end'):
            if request.POST.get('k_start'):
                k_start = int(request.POST.get('k_start'))
            if request.POST.get('k_end'):
                k_end = int( request.POST.get('k_end'))

            x_base = [i for i in range(k_start,k_end+1)]

            data_customers = Customer.objects.filter(id_company = currentuser['id_company']).values()
            orders = Order.objects.filter(id_company = currentuser['id_company']).values()
            data=[[],[],[],[]]
            current_date = date(2022,1,1)
            for d in data_customers:
                length_date = d['last_active'].date()
                for order in orders:
                    if d['id_customer'] == order['id_customer']:
                        if order['date'] < length_date:
                            length_date = order['date']
                
                data[0].append(abs(length_date - d['last_active'].date()).days)
                data[1].append(abs(d['last_active'].date() - current_date).days)
                data[2].append(d['orders'])
                data[3].append(d['total_spend'])
            
            #session data
            request.session['data_rfm'] = list(map(list, zip(*data[1:])))
            request.session['data_lrfm'] = list(map(list, zip(*data)))
            
            #normalization
            data_norm = MinMaxNorm(data).calculate()
            #data rfm
            data_rfm = data_norm[1:]
            #data rfm
            data_lrfm = data_norm.copy()
            
            #pembobotan rfm
            w_rfm1 = [0.0975, 0.3446, 0.5583]
            data_rfm1 = [list(data*w_rfm1[i]) for i, data in enumerate(np.array(data_rfm))]
            w_rfm2 = [0.059, 0.280, 0.670]
            data_rfm2 = [list(data*w_rfm2[i]) for i, data in enumerate(np.array(data_rfm))]
            w_rfm3 = [0.0594, 0.4507, 0.4899]
            data_rfm3 = [list(data*w_rfm3[i]) for i, data in enumerate(np.array(data_rfm))]

            #pembobotan lrfm
            w_lrfm1 = [0.238, 0.088, 0.326, 0.348]
            data_lrfm1 = [list(data*w_lrfm1[i]) for i, data in enumerate(np.array(data_lrfm))]
            w_lrfm2 = [0.222, 0.182, 0.305, 0.292]
            data_lrfm2 = [list(data*w_lrfm2[i]) for i, data in enumerate(np.array(data_lrfm))]
            w_lrfm3 = [0.0405, 0.0747, 0.3155, 0.5691]
            data_lrfm3 = [list(data*w_lrfm3[i]) for i, data in enumerate(np.array(data_lrfm))]

            #silhouette coefficient rfm
            data_sc_rfm = [[], [], [],[]]
            max_sc_rfm = 0
            centroid_rfm = []
            mix_data_rfm = [data_rfm1, data_rfm2, data_rfm3, data_rfm]
            for i, datatest in enumerate(mix_data_rfm):
                for j in range(k_start,k_end+1):
                    km = Kmeans(data = datatest, k=j, max_iter=30).calculate()
                    sc = SilhouetteCoefficient(km['clusters'], datatest)
                    data_sc_rfm[i].append(sc.avg_score)
                    if sc.avg_score > max_sc_rfm:
                        centroid_rfm = km['centroids']
                        max_sc_rfm = sc.avg_score
                        request.session['avg_score_rfm'] = sc.avg_score
                        request.session['clusters_rfm'] = km['clusters']
                        request.session['centroids_rfm'] = km['centroids']
                        request.session['data_weight_rfm'] = mix_data_rfm[i]
                        request.session['score_si_rfm'] = sc.score_si

            
            graph_sc_rfm = testing_sc_bar(x_base, data_sc_rfm, "Silhouette Coeffiennt RFM")
            print(data_sc_rfm)
            print(centroid_rfm)

            # silhouette coefficient lrfm
            data_sc_lrfm = [[], [], [], []]
            max_sc_lrfm = 0
            centroid_lrfm = []
            mix_data_lrfm = [data_lrfm1, data_lrfm2, data_lrfm3, data_lrfm]
            for i, datatest in enumerate(mix_data_lrfm):
                for j in range(k_start,k_end+1):
                    km = Kmeans(data = datatest, k=j, max_iter=30).calculate()
                    sc = SilhouetteCoefficient(km['clusters'], datatest)
                    data_sc_lrfm[i].append(sc.avg_score)
                    if sc.avg_score > max_sc_lrfm:
                        centroid_lrfm = km['centroids']
                        max_sc_lrfm = sc.avg_score
                        request.session['avg_score_lrfm'] = sc.avg_score
                        request.session['clusters_lrfm'] = km['clusters']
                        request.session['centroids_lrfm'] = km['centroids']
                        request.session['data_weight_lrfm'] = mix_data_lrfm[i]
                        request.session['score_si_lrfm'] = sc.score_si
                        
            
            graph_sc_lrfm = testing_sc_bar(x_base, data_sc_lrfm, "Silhouette Coeffiennt LRFM")
            print(data_sc_lrfm)
            print(centroid_lrfm)

            context['k_start'] = k_start
            context['data_sc_rfm'] = list(map(list, zip(*data_sc_rfm)))
            context['graph_sc_rfm'] = graph_sc_rfm
            context['centroid_rfm'] = centroid_rfm

            context['data_sc_lrfm'] = list(map(list, zip(*data_sc_lrfm)))
            context['graph_sc_lrfm'] = graph_sc_lrfm
            context['centroid_lrfm'] = centroid_lrfm            

        return render(request, 'clustering/testing/index.html', context)
    else:
        return redirect('login')


def validate_topsis(preferensi, manual_rank):
    pref_rank = np.array(preferensi)
    pref_rank = pref_rank[pref_rank[:,-1].argsort()]
    validasi = []
    if(len(preferensi) == len(manual_rank)):
        for i, rangking in enumerate(pref_rank):
            if rangking[0] == manual_rank[i]:
                validasi.append([rangking[0], manual_rank[i], 'Valid', 1])
            else:
                validasi.append([rangking[0], manual_rank[i], 'Tidak Valid', 0])
        accuracy = np.array(validasi)[:,-1].astype(np.int).sum()/len(validasi)*100
        return {'result':validasi, 'accuracy':accuracy}
    else:
        return {'result':[], 'accuracy':None}

def testing_volumedata(request):

    if request.session.has_key('user'):
        currentuser = request.session['user']
        context = {
            'title' : 'Pengujian Volume Data',
            'isTestingVolumeData' : True
        }

        if request.POST.get('running'):
            data_customers = Customer.objects.filter(id_company = currentuser['id_company']).values()
            orders = Order.objects.filter(id_company = currentuser['id_company']).values()
            data=[[],[],[],[]]
            current_date = date(2022,1,1)
            for d in data_customers:
                length_date = d['last_active'].date()
                for order in orders:
                    if d['id_customer'] == order['id_customer']:
                        if order['date'] < length_date:
                            length_date = order['date']
                
                data[0].append(abs(length_date - d['last_active'].date()).days)
                data[1].append(abs(d['last_active'].date() - current_date).days)
                data[2].append(d['orders'])
                data[3].append(d['total_spend'])
        
            #data rfm
            data_rfm = data[1:]
            #data rfm
            data_lrfm = data.copy()

            #split data
            persen_data = [ int(round(len(data_customers)*(i/10),0)) for i in range(1,11)]
            data_test_rfm = []
            data_test_lrfm = []
            for persen in persen_data:
                data_test_rfm.append([data_rfm[0][:persen], data_rfm[1][:persen], data_rfm[2][:persen]])
                data_test_lrfm.append([data_lrfm[0][:persen], data_lrfm[1][:persen], data_lrfm[2][:persen], data_lrfm[3][:persen]])
            
            #norm data
            for i in range(len(persen_data)):
                data_test_rfm[i] = MinMaxNorm(data_test_rfm[i]).calculate()
                data_test_lrfm[i] = MinMaxNorm(data_test_lrfm[i]).calculate()

            #pengujian volume data rfm
            si_volumedata_rfm = [ {'volume':i*10, 'k':0, 'si':0} for i in range(1,len(data_test_rfm)+1)]
            for i, datatest in enumerate(data_test_rfm):
                max_si = 0
                for j in range(2,7):
                    km = Kmeans(data = datatest, k=j, max_iter=30).calculate()
                    sc = SilhouetteCoefficient(km['clusters'], datatest)
                    if max_si < sc.avg_score:
                        max_si = sc.avg_score
                        si_volumedata_rfm[i]['k'] = j
                        si_volumedata_rfm[i]['si'] = sc.avg_score
            print(si_volumedata_rfm)

            #pengujian volume data lrfm
            si_volumedata_lrfm = [ {'volume':i*10, 'k':0, 'si':0} for i in range(1,len(data_test_lrfm)+1)]
            for i, datatest in enumerate(data_test_lrfm):
                max_si = 0
                for j in range(2,7):
                    km = Kmeans(data = datatest, k=j, max_iter=30).calculate()
                    sc = SilhouetteCoefficient(km['clusters'], datatest)
                    if max_si < sc.avg_score:
                        max_si = sc.avg_score
                        si_volumedata_lrfm[i]['k'] = j
                        si_volumedata_lrfm[i]['si'] = sc.avg_score
            print(si_volumedata_lrfm)

            #bar chart
            x = [str(i*10)+"%" for i in range(1,11)]
            y1=[]
            y2=[]
            for i in range(len(persen_data)):
                y1.append(si_volumedata_rfm[i]['si'])
                y2.append(si_volumedata_lrfm[i]['si'])

            graph_vd = grouped_two_bar(x, y1, y2, "Persentase Data", "Score", "RFM", "LRFM", "Silhouette Coefficient Pada Variasi Volume Data")


            context['si_volumedata_rfm'] = si_volumedata_rfm
            context['si_volumedata_lrfm'] = si_volumedata_lrfm
            context['graph_vd'] = graph_vd

        return render(request, 'clustering/testing/testing_volumedata.html', context)
    else:
        return redirect('login')

def testing_validasitopsis(request):
    if request.session.has_key('user'):
        currentuser = request.session['user']
        context = {
            'title': 'Skenario 3',
            'isValidasiTopsis': True,
            'session_data': False
        }
        centroid_rfm =  request.session['centroids_rfm'] if request.session.has_key('centroids_rfm') else False
        centroid_lrfm = request.session['centroids_lrfm'] if request.session.has_key('centroids_lrfm') else False
        context['session_data'] = True if centroid_rfm and centroid_lrfm else False
        
        if request.POST.get('running'):
            if centroid_rfm and centroid_lrfm:
                #topsis rfm
                alternative_label = ['Cluster '+str(i+1) for i in range(len(centroid_rfm))]
                label_topsis = ['r','f','m']
                benefit = ['f', 'm']
                cost = ['r']
                data_topsis_rfm={}
                for j in range(len(centroid_rfm[0])):
                    temp=[]
                    for i in range(len(centroid_rfm)):
                        temp.append(centroid_rfm[i][j])
                    data_topsis_rfm[label_topsis[j]] = temp
                
                request.session['data_topsis_rfm'] = data_topsis_rfm

                t_rfm = Topsis(data=data_topsis_rfm, benefit=benefit, cost=cost,alternative=alternative_label)
                preferensiRfm = t_rfm.preferensi()
                request.session['preferensi_rfm'] = [[data[0], data[1], int(data[2])] for data in preferensiRfm]
                print(preferensiRfm)

                #validasi rfm
                manual_rank_rfm = ['Cluster 2', 'Cluster 1']
                validasi_rfm = validate_topsis(preferensiRfm, manual_rank_rfm)
                request.session['validasi_rfm'] = validasi_rfm["accuracy"] 
                print(validasi_rfm)

                #topsis lrfm
                alternative_label = ['Cluster '+str(i+1) for i in range(len(centroid_rfm))]
                label_topsis = ['l','r','f','m']
                benefit = ['f', 'm']
                cost = ['l','r']
                data_topsis_lrfm={}
                for j in range(len(centroid_lrfm[0])):
                    temp=[]
                    for i in range(len(centroid_lrfm)):
                        temp.append(centroid_lrfm[i][j])
                    data_topsis_lrfm[label_topsis[j]] = temp
                
                request.session['data_topsis_lrfm'] = data_topsis_lrfm
                t_lrfm = Topsis(data=data_topsis_lrfm, benefit=benefit, cost=cost,alternative=alternative_label)
                preferensiLrfm = t_lrfm.preferensi()
                request.session['preferensi_lrfm'] = [[data[0], data[1], int(data[2])] for data in preferensiLrfm]
                print(preferensiLrfm)

                #validasi rfm
                manual_rank_lrfm = ['Cluster 2', 'Cluster 1']
                validasi_lrfm = validate_topsis(preferensiLrfm, manual_rank_lrfm)
                request.session['validasi_lrfm'] = validasi_lrfm["accuracy"]
                print(validasi_lrfm)

                context['centroid_rfm'] = centroid_rfm
                context['centroid_lrfm'] = centroid_lrfm
                context['preferensiRfm'] = preferensiRfm
                context['preferensiLrfm'] = preferensiLrfm
                context['validasi_rfm'] = validasi_rfm
                context['validasi_lrfm'] = validasi_lrfm

        return render(request, 'clustering/testing/testing_validasitopsis.html', context)
    else:
        return redirect('login')

def testing_rankconsistency(request):
    if request.session.has_key('user'):
        currentuser = request.session['user']
        context = {
            'title': 'Skenario 4',
            'isRankConsistency': True,
            'session_data' :False
        }

        data_topsis_rfm =  request.session['data_topsis_rfm'] if request.session.has_key('data_topsis_rfm') else False
        data_topsis_lrfm = request.session['data_topsis_lrfm'] if request.session.has_key('data_topsis_lrfm') else False
        context['session_data'] = True if data_topsis_rfm and data_topsis_lrfm else False

        if request.POST.get('running'):
            if data_topsis_rfm and data_topsis_lrfm:
                #rank consistency rfm
                benefit = ['f', 'm']
                cost = ['r']
                len_centroid_rfm = len(data_topsis_rfm['r'])
                label = ['Cluster '+str(i+1) for i in range(len_centroid_rfm)]
                t_rfm = Topsis(data=data_topsis_rfm, benefit=benefit, cost=cost,alternative=label)
                top_pref_rfm = t_rfm.top_pref
                low_pref_rfm = t_rfm.low_pref

                data_uji = {}
                consitency = []
                matrix_rankConsistencyRfm=[]
                for i in range(len_centroid_rfm):
                    data_uji = data_uji.clear()
                    data_uji = deepcopy(data_topsis_rfm)
                    alternative_test = []
                    for k, v in data_topsis_rfm.items():            
                        data_uji[k].append(v[i])
                    
                    alternative_test = ['Cluster '+str(i+1) for i in range(len_centroid_rfm)]
                    alternative_test.append('Alternatif Cluster '+str(i+1))
                        
                    c = Topsis(data=data_uji, benefit=benefit, cost=cost, alternative=alternative_test)        
                    print('Add alternatif ' + str(i))
                    print(c.preferensi())
                    matrix_rankConsistencyRfm.append(c.preferensi())

                    if top_pref_rfm == c.top_pref and low_pref_rfm == c.low_pref:
                        consitency.append(1)
                    else:
                        consitency.append(0)
                print('Akurasi Rank Consistency : '+ str(sum(consitency)/len(consitency)*100)+'%')
                accuracy_rankConsistencyRfm = sum(consitency)/len(consitency)*100
                request.session['rc_rfm'] = accuracy_rankConsistencyRfm

                #rank consistenct lrfm
                benefit = ['f', 'm']
                cost = ['l','r']
                len_centroid_lrfm = len(data_topsis_rfm['r'])
                label = ['Cluster '+str(i+1) for i in range(len_centroid_lrfm)]
                t_lrfm = Topsis(data=data_topsis_lrfm, benefit=benefit, cost=cost,alternative=label)
                top_pref_lrfm = t_lrfm.top_pref
                low_pref_lrfm = t_lrfm.low_pref

                data_uji = {}
                consitency = []
                matrix_rankConsistencyLrfm=[]
                for i in range(len_centroid_lrfm):
                    data_uji = data_uji.clear()
                    data_uji = deepcopy(data_topsis_lrfm)
                    alternative_test = []
                    for k, v in data_topsis_lrfm.items():            
                        data_uji[k].append(v[i])
                    
                    alternative_test = ['Cluster '+str(i+1) for i in range(len_centroid_lrfm)]
                    alternative_test.append('Alternatif Cluster '+str(i+1))
                        
                    c = Topsis(data=data_uji, benefit=benefit, cost=cost, alternative=alternative_test)        
                    print('Add alternatif ' + str(i))
                    print(c.preferensi())
                    matrix_rankConsistencyLrfm.append(c.preferensi())

                    if top_pref_lrfm == c.top_pref and low_pref_lrfm == c.low_pref:
                        consitency.append(1)
                    else:
                        consitency.append(0)
                print('Akurasi Rank Consistency : '+ str(sum(consitency)/len(consitency)*100)+'%')
                accuracy_rankConsistencyLrfm = sum(consitency)/len(consitency)*100
                request.session['rc_lrfm'] = accuracy_rankConsistencyLrfm


                context['matrix_rankConsistencyRfm'] = matrix_rankConsistencyRfm
                context['accuracy_rankConsistencyRfm'] = accuracy_rankConsistencyRfm
                context['matrix_rankConsistencyLrfm'] = matrix_rankConsistencyLrfm
                context['accuracy_rankConsistencyLrfm'] = accuracy_rankConsistencyLrfm

        return render(request, 'clustering/testing/testing_rankconsistency.html', context)
    else:
        return redirect('login')