from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Producto


def inicio(request):
    productos = Producto.objects.filter(
        activo=True,
        destacado=True
    )

    return render(request, 'tienda/inicio.html', {
        'productos': productos
    })


def catalogo(request):
    categoria = request.GET.get('categoria')

    productos = Producto.objects.filter(activo=True)

    if categoria:
        productos = productos.filter(categoria=categoria)

    return render(request, 'tienda/catalogo.html', {
        'productos': productos,
        'categoria_actual': categoria
    })


def detalle_producto(request, id):
    producto = Producto.objects.get(id=id)

    return render(request, 'tienda/detalle_producto.html', {
        'producto': producto
    })


def carrito(request):
    carrito = request.session.get('carrito', {})

    productos = Producto.objects.filter(
        id__in=carrito.keys(),
        activo=True
    )

    productos_carrito = []

    total = 0

    for producto in productos:

        cantidad = carrito.get(str(producto.id), 0)

        subtotal = producto.precio * cantidad

        total += subtotal

        productos_carrito.append({
            'producto': producto,
            'cantidad': cantidad,
            'subtotal': subtotal,
        })

    return render(request, 'tienda/carrito.html', {
        'productos_carrito': productos_carrito,
        'total': total
    })


def agregar_carrito(request, id):
    carrito = request.session.get('carrito', {})

    id = str(id)

    if id in carrito:
        carrito[id] += 1
    else:
        carrito[id] = 1

    request.session['carrito'] = carrito
    request.session.modified = True

    return redirect('carrito')

def actualizar_carrito(request, id):

    carrito = request.session.get('carrito', {})

    id = str(id)

    if request.method == 'POST':

        cantidad = int(request.POST.get('cantidad', 1))

        if cantidad > 0:
            carrito[id] = cantidad
        else:
            carrito.pop(id, None)

    request.session['carrito'] = carrito
    request.session.modified = True

    return redirect('carrito')