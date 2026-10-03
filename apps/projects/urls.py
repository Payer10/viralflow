from django.urls import path
from .views import*

urlpatterns = [
    path('', projects_view, name='projects')
]