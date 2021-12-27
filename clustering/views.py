from django.shortcuts import render

# Create your views here.
def index(request):
    context ={
        'title':'Clustering'
    }
    return render(request,'clustering/index.html',context)