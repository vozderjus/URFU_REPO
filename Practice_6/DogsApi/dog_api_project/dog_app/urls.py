# dog_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/breeds/', views.get_all_breeds_api, name='get_all_breeds'),
    path('api/images/', views.get_breed_images_api, name='get_breed_images'),
]