from django.shortcuts import redirect, render

def dashboard(request):
    context = {
        'title' : 'Dashboard',
        'isDashboard':True
    }
    return render(request, 'clustering/dashboard/index.html', context)