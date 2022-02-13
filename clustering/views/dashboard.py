from tkinter.tix import MAX
from django.shortcuts import redirect, render
from clustering.models import Customer, Order
from django.db.models import Max, Min, Sum
from clustering.utils import sales_plot

def dashboard(request):
    if request.session.has_key("user"):
        current_user = request.session['user']
        data_customer = Customer.objects.filter(id_company = current_user['id_company'])
        data_order = Order.objects.filter(id_company = current_user['id_company'], status = 'Completed')
        cluster = 0 if data_customer.aggregate(Max('cluster'))['cluster__max'] == None else data_customer.aggregate(Max('cluster'))['cluster__max']
        
        context = {
            'title' : 'Dashboard',
            'isDashboard':True,
            'customer_count' : len(data_customer),
            'order_count' : len(data_order),
            'cluster' : cluster
        }
        max_date = data_order.aggregate(Max('date'))['date__max']
        min_date = data_order.aggregate(Min('date'))['date__min']
        if max_date and min_date:
            years = [i for i in range(min_date.year, max_date.year+1)]
            income = []
            count_order = []
            for year in years:
                income.append(data_order.filter(date__year = year).aggregate(Sum('total'))['total__sum'])
                count_order.append(len(data_order.filter(date__year = year)))

            context['income_plot'] = sales_plot(years, income,'income')
            context['order_plot'] = sales_plot(years, count_order, 'order')           

        return render(request, 'clustering/dashboard/index.html', context)
    else:
        return redirect('login')
