from django.urls import path
from . import views

urlpatterns = [
    path('', views.RestaurantsView.as_view(), name='restaurants'),
]
