from django.http.response import HttpResponse
from django.shortcuts import render

def index(request):
    context={
        'title':'Customer Relationship Management'
    }

    return render(request, 'index.html', context)
