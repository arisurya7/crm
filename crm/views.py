from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from clustering.models import UserCompany

def index(request):
    context={
        'title':'Customer Relationship Management'
    }

    return render(request, 'index.html', context)

def login(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        pwd = request.POST.get('password')

        checkuser = UserCompany.objects.filter(username = uname, password = pwd, verified__isnull = False).values()
        if checkuser:
            request.session['user'] = checkuser[0]
            return redirect('clustering:dashboard')
    context={
        'title':'Login'
    }
    return render(request, 'login.html', context)

