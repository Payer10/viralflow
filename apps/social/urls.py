from django.urls import path
from .views import*

urlpatterns = [
    path('', social_view, name='social')
]