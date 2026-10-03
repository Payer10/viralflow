from django.urls import path
from .views import*

urlpatterns = [
    path('', credits_view, name='credits')
]