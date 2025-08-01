from django.urls import path
from . import views

urlpatterns = [
    path('', views.MenusView.as_view(), name='menus'),
    path('<str:pk>/', views.MenusView.as_view(), name='menu-detail'),
]
