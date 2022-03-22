from django.shortcuts import render, redirect
from clustering.utils import threedim_scatter_plot, silhouette_bar
from .checkmodel import checkTypeModel, checkSilhouetteStructure

def rekomendasi(request):

    if request.session.has_key('user'):
        current_user = request.session['user']
        context = {
            'title' : 'Rekomendasi',
            'isRekomendasi' : True
        }

        if request.session.has_key('clusters_rfm') and request.session.has_key('centroids_rfm') and request.session.has_key('data_weight_rfm') and request.session.has_key('score_si_rfm'):
            scatter_rfm = threedim_scatter_plot(data_param = request.session['data_weight_rfm'], labels = request.session['clusters_rfm'], title_scatter = 'Scatter Plot Cluster RFM')
            sc_rfm = silhouette_bar(score_si = request.session['score_si_rfm'], labels = request.session['clusters_rfm'], title_sc = "Silhouette plot for the various clusters RFM")
            
            member_sc_rfm = []
            score_si_rfm = request.session['score_si_rfm']
            for j in range(max(list(request.session['clusters_rfm']))+1):
                si_status = {}
                no_stucture = 0
                weak_stucture = 0
                medium_stucture = 0
                strong_stucture = 0
                for index, data in enumerate(request.session['clusters']):
                    if j == data: 
                        iter+=1
                        if checkSilhouetteStructure(score_si_rfm[index])=='No Structure':
                            no_stucture+=1
                        elif checkSilhouetteStructure(score_si_rfm[index])=='Weak Structure':
                            weak_stucture+=1
                        elif checkSilhouetteStructure(score_si_rfm[index])=='Medium Structure':
                            medium_stucture+=1
                        elif checkSilhouetteStructure(score_si_rfm[index])=='Strong Structure':
                            strong_stucture+=1

                si_status['strong_structure'] = strong_stucture
                si_status['medium_structure'] = medium_stucture
                si_status['weak_structure'] = weak_stucture
                si_status['no_structure'] = no_stucture
                member_sc_rfm.append(si_status)
                
            context['scatter_rfm'] = scatter_rfm
            context['sc_rfm'] = sc_rfm
            print('session rfm available')
        
        if request.session.has_key('clusters_lrfm') and request.session.has_key('centroids_lrfm') and request.session.has_key('data_weight_lrfm') and request.session.has_key('score_si_lrfm'):
            scatter_lrfm = threedim_scatter_plot(data_param = request.session['data_weight_lrfm'], labels = request.session['clusters_lrfm'], title_scatter = 'Scatter Plot Cluster LRFM')
            sc_lrfm = silhouette_bar(score_si = request.session['score_si_lrfm'], labels = request.session['clusters_lrfm'], title_sc = "Silhouette plot for the various clusters LRFM")
            context['scatter_lrfm'] = scatter_lrfm
            context['sc_lrfm'] = sc_lrfm
            print('session lrfm available')
        
        return render(request, 'clustering/rekomendasi/index.html', context)
    else:
        return redirect('login')
    