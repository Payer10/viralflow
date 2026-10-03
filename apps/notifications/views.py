from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


def notifications_view(request):
    return HttpResponse("Hello, Notifications!")