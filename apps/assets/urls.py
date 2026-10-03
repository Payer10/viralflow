from django.urls import path
from .views import*

urlpatterns = [
    path('', assets_view, name='assets')
]