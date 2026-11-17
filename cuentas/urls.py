from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('entrar/', views.EntrarView.as_view(), name='entrar'),
    path('salir/', auth_views.LogoutView.as_view(), name='salir'),
    path('mi-cuenta/', views.mi_cuenta, name='mi_cuenta'),
]
