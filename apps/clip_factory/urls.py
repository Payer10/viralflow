from django.urls import path
from .views import*

urlpatterns = [
    path('', clip_factory_view, name='clip_factory')
]