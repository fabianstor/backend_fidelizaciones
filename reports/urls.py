from django.urls import path
from . import views

urlpatterns = [
    path('restaurant_dashboard/', views.ReportsView.as_view(), name='reports-dashboard'),
    path('admin_dashboard/', views.AdminReportsView.as_view(), name='reports-admin-dashboard'),
]
