from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.



def projects_view(request):
    return HttpResponse("Hello, Projects!")