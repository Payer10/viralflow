from django.urls import path
from .views import*

urlpatterns = [
    path('', exports_view, name='exports')
]