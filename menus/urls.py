from django.urls import path
from . import views

urlpatterns = [
    path('', views.MenusView.as_view(), name='menus'),
]
