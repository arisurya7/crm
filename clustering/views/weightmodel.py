from django.shortcuts import redirect, render
from clustering.models import Customer,WeightLRFM, WeightRFM
from django.contrib import messages
from clustering.algorithm.ahp import AhpWeight


def weightmodel(request):
    if request.session.has_key("user"):
        currentuser = request.session['user']
        weigth_rfm = WeightRFM.objects.filter(id_company = currentuser['id_company']).values()
        weigth_lrfm = WeightLRFM.objects.filter(id_company = currentuser['id_company']).values()

        context = {
            'title' : 'Weight Model',
            'isWeightModel':True,
            'weight_rfm' : weigth_rfm[0],
            'weight_lrfm' : weigth_lrfm[0],
            'role' : currentuser['role'],
        }
        return render(request, 'clustering/weightmodel/index.html', context)
    else:
        return redirect('login')

def calculateahp(request):
    if request.session.has_key("user"):
        currentuser = request.session['user']
        data_input = {}
        if request.POST:
            if request.POST.get('score6'):
                data_input[request.POST.get('input1')] = int(request.POST.get('score1'))
                data_input[request.POST.get('input2')] = int(request.POST.get('score2'))
                data_input[request.POST.get('input3')] = int(request.POST.get('score3'))
                data_input[request.POST.get('input4')] = int(request.POST.get('score4'))
                data_input[request.POST.get('input5')] = int(request.POST.get('score5'))
                data_input[request.POST.get('input6')] = int(request.POST.get('score6'))
                criteria = ['l','r','f','m']
            else:
                data_input[request.POST.get('input1')] = int(request.POST.get('score1'))
                data_input[request.POST.get('input2')] = int(request.POST.get('score2'))
                data_input[request.POST.get('input3')] = int(request.POST.get('score3'))
                criteria = ['r','f','m']

        if(len(data_input)>0):
            ahp = AhpWeight(data_input, criteria)
            if(ahp.consistency_ratio < 0.1):
                weight = ahp.final_weight
                if request.POST.get('score6'):
                    print(weight)
                    db_weight = WeightLRFM.objects.filter(id_company = currentuser['id_company']).get(id = request.POST.get('id_weight'))
                    print(db_weight)
                    db_weight.w_length = weight['l']
                    db_weight.w_recency = weight['r']
                    db_weight.w_frequency = weight['f']
                    db_weight.w_monetary = weight['m']
                    db_weight.score_input = str(ahp.comparison_matrix)
                    db_weight.save()
                    messages.info(request, 'success')
                else:
                    print(weight)
                    db_weight = WeightRFM.objects.filter(id_company = currentuser['id_company']).get(id = request.POST.get('id_weight'))
                    print(db_weight)
                    db_weight.w_recency = weight['r']
                    db_weight.w_frequency = weight['f']
                    db_weight.w_monetary = weight['m']
                    db_weight.score_input = str(ahp.comparison_matrix)
                    db_weight.save()
                    messages.info(request, 'success')

            else:
                messages.info(request, 'Please re-submit, because consintency ration more than 0.1')
        return redirect('clustering:weightmodel')
    else:
        return redirect('login')
