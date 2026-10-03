from django.urls import path
from .views import*

urlpatterns = [
    path('', face_swap_view, name='face_swap')
]