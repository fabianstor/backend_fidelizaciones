from django.urls import path
from . import views

urlpatterns = [
    path('', views.RestaurantsView.as_view(), name='restaurants'),
    path('<str:restaurant_id>/', views.RestaurantsView.as_view(), name='restaurant-detail'),
]
