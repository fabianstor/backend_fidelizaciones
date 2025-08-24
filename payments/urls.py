from django.urls import path
from . import views

urlpatterns = [
    path('payment-request', views.PaymentsView.as_view(), name='payments'),
]
