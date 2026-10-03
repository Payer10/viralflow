from django.urls import path
from .views import*

urlpatterns = [
    path('', viral_clone_view, name='viral_clone'),
]