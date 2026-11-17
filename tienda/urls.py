from django.urls import path
from . import views

urlpatterns = [

    path('', views.inicio, name='inicio'),

    path('catalogo/', views.catalogo, name='catalogo'),

    path('producto/<int:id>/', views.detalle_producto, name='detalle_producto'),

    path('carrito/', views.carrito, name='carrito'),

    path(
        'carrito/agregar/<int:id>/',
        views.agregar_carrito,
        name='agregar_carrito'
    ),

    path(
        'carrito/actualizar/<int:id>/',
        views.actualizar_carrito,
        name='actualizar_carrito'
    ),

]