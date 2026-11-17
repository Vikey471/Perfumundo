from django.urls import path

from . import views

urlpatterns = [
    path('finalizar-compra/', views.checkout, name='checkout'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('mis-pedidos/<int:pk>/', views.detalle_pedido, name='detalle_pedido'),
]
