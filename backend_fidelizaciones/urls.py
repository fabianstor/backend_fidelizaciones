"""
URL configuration for backend_fidelizaciones project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include

from backend_fidelizaciones.login import FirebaseLoginView

api_patterns = [
    path('firebase-login/', FirebaseLoginView.as_view(), name='firebase-auth'),
    path('users/', include('users.urls')),
    path('restaurants/', include('restaurants.urls')),
    path('menus/', include('menus.urls')),
    path('payments/', include('payments.urls')),
]

urlpatterns = [
    path('api/', include(api_patterns)),
]
