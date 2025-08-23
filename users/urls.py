from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CreateUserAPIView.as_view(), name='crear_usuario'),
    path('update/<str:pk>/', views.CreateUserAPIView.as_view(), name='actualizar_usuario'),
]
