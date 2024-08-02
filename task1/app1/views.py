from django.shortcuts import render

from django.http import HttpResponse

def home(request):
    return HttpResponse("WELCOME, To the Django Web Application")

def startbutton(request):
    return render(request,'home.html')

# Create your views here.
