from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def face_swap_view(request):
    return HttpResponse("Hello, Face Swap!")