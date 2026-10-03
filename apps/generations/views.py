from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def generations_view(request):
    return HttpResponse("Hello, Generations!")