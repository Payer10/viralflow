from django.urls import path
from .views import*

urlpatterns = [
    path('', generations_view, name='generations')
]