from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def viral_clone_view(request):
    return HttpResponse("Hello, Viral Clone!")