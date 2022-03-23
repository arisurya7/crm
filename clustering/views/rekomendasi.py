from datetime import datetime
from django.shortcuts import render, redirect
from numpy import character
from clustering.utils import threedim_scatter_plot, silhouette_bar, persentage_horizontal_bar, hours_bar, pie_chart
from .checkmodel import checkTypeModel, checkSilhouetteStructure
from clustering.models import Customer, Order

def rekomendasi(request):

    if request.session.has_key('user'):
        currentuser = request.session['user']
        context = {
            'title' : 'Rekomendasi',
            'isRekomendasi' : True
        }

        if request.session.has_key('clusters_rfm') and request.session.has_key('centroids_rfm') and request.session.has_key('data_weight_rfm') and request.session.has_key('score_si_rfm'):
            scatter_rfm = threedim_scatter_plot(data_param = request.session['data_weight_rfm'], labels = request.session['clusters_rfm'], title_scatter = 'Scatter Plot Cluster RFM')
            sc_rfm = silhouette_bar(score_si = request.session['score_si_rfm'], labels = request.session['clusters_rfm'], title_sc = "Silhouette plot for the various clusters RFM")
            member_sc_rfm = countMemberByModel(request.session['score_si_rfm'], request.session['clusters_rfm'])
            total_member_sc_rfm = [sum(map(lambda x: x['strong_structure'], member_sc_rfm)), sum(map(lambda x: x['medium_structure'], member_sc_rfm)), sum(map(lambda x: x['weak_structure'], member_sc_rfm)), sum(map(lambda x: x['no_structure'], member_sc_rfm))]
            context['scatter_rfm'] = scatter_rfm
            context['sc_rfm'] = sc_rfm
            context['member_sc_rfm'] = member_sc_rfm
            context['total_member_sc_rfm'] = total_member_sc_rfm
            print('session rfm available')
        
        if request.session.has_key('clusters_lrfm') and request.session.has_key('centroids_lrfm') and request.session.has_key('data_weight_lrfm') and request.session.has_key('score_si_lrfm'):
            scatter_lrfm = threedim_scatter_plot(data_param = request.session['data_weight_lrfm'], labels = request.session['clusters_lrfm'], title_scatter = 'Scatter Plot Cluster LRFM')
            sc_lrfm = silhouette_bar(score_si = request.session['score_si_lrfm'], labels = request.session['clusters_lrfm'], title_sc = "Silhouette plot for the various clusters LRFM")
            member_sc_lrfm = countMemberByModel(request.session['score_si_lrfm'], request.session['clusters_lrfm'])
            total_member_sc_lrfm = [sum(map(lambda x: x['strong_structure'], member_sc_lrfm)), sum(map(lambda x: x['medium_structure'], member_sc_lrfm)), sum(map(lambda x: x['weak_structure'], member_sc_lrfm)), sum(map(lambda x: x['no_structure'], member_sc_lrfm))]
            
            context['scatter_lrfm'] = scatter_lrfm
            context['sc_lrfm'] = sc_lrfm
            context['member_sc_lrfm'] = member_sc_lrfm
            context['total_member_sc_lrfm'] = total_member_sc_lrfm
            print('session lrfm available')

        clusters = []
        centroids = []
        data_weight = []
        score_si = []

        if request.session.has_key('avg_score_rfm') and request.session.has_key('avg_score_lrfm'):
            if request.session['avg_score_rfm'] > request.session['avg_score_lrfm']:
                clusters = request.session['clusters_rfm']
                centroids = request.session['centroids_rfm']
                data_weight = request.session['data_weight_rfm']
                score_si = request.session['score_si_rfm']
            else:
                clusters = request.session['clusters_lrfm']
                centroids = request.session['centroids_lrfm']
                data_weight = request.session['data_weight_lrfm']
                score_si = request.session['score_si_lrfm']
            
            
            data_customers = Customer.objects.filter(id_company = currentuser['id_company']).values()
            orders = Order.objects.filter(id_company = currentuser['id_company']).values()
            
            #Devide data region, hours by cluster
            countries = [{'domestik':0, 'manca negara':0} for i in range(max(clusters)+1)]
            regions = [{} for i in range(max(clusters)+1)]
            hours = [{} for i in range(max(clusters)+1)]
            id_customers = [[] for i in range(max(clusters)+1)]
            for i in range(len(clusters)):
                for j in range(max(clusters)+1):
                    if j == clusters[i]:
                        id_customers[j].append(data_customers[i]['id_customer'])
                        #Country
                        if data_customers[i]['country'] == "ID":
                            countries[j]["domestik"] += 1
                        else:
                            countries[j]["manca negara"] += 1

                        #Region
                        if data_customers[i]['region'] not in regions[j].keys():
                            regions[j][data_customers[i]['region']] = 1
                        else:
                            regions[j][data_customers[i]['region']] +=1
                        
                        #Hours
                        if data_customers[i]['last_active'].hour not in hours[j].keys():
                            hours[j][data_customers[i]['last_active'].hour] = 1
                        else:
                            hours[j][data_customers[i]['last_active'].hour] += 1
                        
                        break
            
            #Devide data month by cluster
            month = [{} for i in range(max(clusters)+1)]
            month_category = [{'awal bulan':0, 'tengah bulan':0, 'akhir bulan':0} for i in range(max(clusters)+1)]
            for order in orders:
                for j, ids in enumerate(id_customers):
                    if order['id_customer'] in ids:
                        if order['date'].month not in month[j].keys():
                            month[j][order['date'].month] = 1
                        else:
                            month[j][order['date'].month] += 1
                        
                        if order['date'].day < 8:
                            month_category[j]['awal bulan'] += 1
                        elif order['date'].day > 23:
                            month_category[j]['akhir bulan'] += 1
                        else:
                            month_category[j]['tengah bulan'] += 1

                        break
            
            #Get category time by cluster
            category_time = [{'pagi':0, 'siang':0, 'sore':0, 'malam':0, 'dinihari':0} for i in range(max(clusters)+1)]
            for i, value in enumerate(hours):
                for k,v in value.items():
                    if k > 0 and k < 5:
                        category_time[i]['dinihari'] = category_time[i]['dinihari'] + v
                    elif k >= 5 and k < 11:
                        category_time[i]['pagi'] = category_time[i]['pagi'] + v
                    elif k >= 11 and k < 15:
                        category_time[i]['siang'] = category_time[i]['siang'] + v
                    elif k >= 15 and k < 19:
                        category_time[i]['sore'] = category_time[i]['sore'] + v         
                    else:
                        category_time[i]['malam'] = category_time[i]['malam']+v
            
            regions_sort = sortDataByValues(regions)
            hours_sort = sortDataByKeys(hours)
            month_sort = sortDataByValues(month)
            

            #Merge Graph
            characteristic_graph = []
            for i in range(max(clusters)+1):
                month_labels = [(datetime.strptime(str(month),"%m")).strftime("%b") for month in month_sort[i]] 
                country_bar = pie_chart(countries[i].values(), countries[i].keys(), "Pelanggan Berdasarkan Kenegaraan", "Kenegaraan", ['dalam negeri', 'luar negeri'])
                regions_bar = persentage_horizontal_bar(list(regions_sort[i].values()), list(regions_sort[i].keys()), x_label='Persentase Jumlah Pelanggan Pada Cluster', y_label='Region', title='Pelanggan Berdasarkan Region')
                month_bar = persentage_horizontal_bar(list(month_sort[i].values()), month_labels, x_label="Persentase Jumlah Pelanggan Pada Cluster", y_label="Bulan", title="Order Berdasarkan Bulan")
                month_category_bar = pie_chart(month_category[i].values(), month_category[i].keys(), "Order Berdasarkan Kategori Bulan", "Tanggal", ['1-7', '8-22','>=23'])
                bar_hours = hours_bar(hours_sort[i].keys(), hours_sort[i].values())
                category_time_bar = pie_chart(category_time[i].values(), category_time[i].keys(), "Transaksi Berdasarkan Kategori Waktu", "Jam", ['5.00 - 10.59', '11.00-14.59','15.00-18.59', '17.00-23.59', '00.00-4.59'])
                characteristic_graph.append([regions_bar, country_bar, month_bar, month_category_bar, bar_hours, category_time_bar])
            
            context['characteristic_graph'] = characteristic_graph
           
           
            print(countries)
            print(id_customers)
            print(category_time)
            
        
        return render(request, 'clustering/rekomendasi/index.html', context)
    else:
        return redirect('login')

def clear_rekomendasi(request):
    try:
        del request.session['avg_score_rfm']
        del request.session['clusters_rfm']
        del request.session['centroids_rfm']
        del request.session['data_weight_rfm']
        del request.session['score_si_rfm']

        del request.session['avg_score_lrfm']
        del request.session['clusters_lrfm']
        del request.session['centroids_lrfm']
        del request.session['data_weight_lrfm']
        del request.session['score_si_lrfm']
    
        return redirect('clustering:rekomendasi')
    except:
        return redirect('clustering:rekomendasi')
    

def countMemberByModel(score_si, clusters):
    member_sc = []
    for j in range(max(list(clusters))+1):
        si_status = {}
        no_stucture = 0
        weak_stucture = 0
        medium_stucture = 0
        strong_stucture = 0
        for index, data in enumerate(clusters):
            if j == data: 
                if checkSilhouetteStructure(score_si[index])=='No Structure':
                    no_stucture+=1
                elif checkSilhouetteStructure(score_si[index])=='Weak Structure':
                    weak_stucture+=1
                elif checkSilhouetteStructure(score_si[index])=='Medium Structure':
                    medium_stucture+=1
                elif checkSilhouetteStructure(score_si[index])=='Strong Structure':
                    strong_stucture+=1

        si_status['strong_structure'] = strong_stucture
        si_status['medium_structure'] = medium_stucture
        si_status['weak_structure'] = weak_stucture
        si_status['no_structure'] = no_stucture
        member_sc.append(si_status)

    return member_sc

def sortDataByValues(data):
    data_sort = []
    for d in data:
        data_sort. append(dict(sorted(d.items(), key=lambda x: x[1], reverse=False)))
    return data_sort
        
def sortDataByKeys(data):
    data_sort = []
    for d in data:
        data_sort. append(dict(sorted(d.items())))
    return data_sort
