from django.urls import path
from . import views

urlpatterns = [
    path('', views.weather_index, name='weather_index'),
    path('<str:city>/', views.weather_detail, name='weather_detail'),
]