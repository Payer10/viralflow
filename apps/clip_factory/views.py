from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def clip_factory_view(request):
    return HttpResponse("Hello, Clip Factory!")