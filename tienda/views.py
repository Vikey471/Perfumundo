from decimal import Decimal

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Marca, Producto


def inicio(request):
    productos = (
        Producto.objects
        .filter(activo=True, destacado=True)
        .select_related('marca')
    )

    return render(request, 'tienda/inicio.html', {
        'productos': productos
    })


def catalogo(request):
    categoria = request.GET.get('categoria') or None
    marca = request.GET.get('marca') or None
    genero = request.GET.get('genero') or None
    concentracion = request.GET.get('concentracion') or None
    busqueda = (request.GET.get('q') or '').strip()

    productos = Producto.objects.filter(activo=True).select_related('marca')
    marcas = Marca.objects.filter(productos__activo=True).distinct()

    if categoria in Marca.Categoria.values:
        productos = productos.filter(marca__categoria=categoria)
        marcas = marcas.filter(categoria=categoria)
    else:
        categoria = None

    if marca:
        productos = productos.filter(marca__slug=marca)

    if genero in Producto.Genero.values:
        productos = productos.filter(genero=genero)
    else:
        genero = None

    if concentracion in Producto.Concentracion.values:
        productos = productos.filter(concentracion=concentracion)
    else:
        concentracion = None

    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) | Q(marca__nombre__icontains=busqueda)
        )

    return render(request, 'tienda/catalogo.html', {
        'productos': productos,
        'busqueda': busqueda,
        'categoria_actual': categoria,
        'marca_actual': marca,
        'genero_actual': genero,
        'concentracion_actual': concentracion,
        'categorias': Marca.Categoria.choices,
        'marcas': marcas,
        'generos': Producto.Genero.choices,
        'concentraciones': Producto.Concentracion.choices,
    })


def detalle_producto(request, slug):
    producto = get_object_or_404(
        Producto.objects
        .select_related('marca')
        .prefetch_related('imagenes'),
        slug=slug,
        activo=True,
    )

    return render(request, 'tienda/detalle_producto.html', {
        'producto': producto,
    })


def _guardar_carrito(request, carrito):
    request.session['carrito'] = carrito
    request.session.modified = True


def carrito(request):
    carrito = request.session.get('carrito', {})

    productos = Producto.objects.filter(
        id__in=carrito.keys(),
        activo=True
    ).select_related('marca')

    productos_carrito = []
    total = Decimal('0')

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


@require_POST
def agregar_carrito(request, id):
    producto = get_object_or_404(Producto, id=id, activo=True)
    carrito = request.session.get('carrito', {})
    clave = str(producto.id)

    cantidad_actual = carrito.get(clave, 0)

    if cantidad_actual + 1 > producto.stock:
        messages.warning(
            request,
            f'No hay más piezas disponibles de {producto.nombre}.'
        )
    else:
        carrito[clave] = cantidad_actual + 1
        _guardar_carrito(request, carrito)
        messages.success(request, f'{producto.nombre} se agregó al carrito.')

    return redirect('carrito')


@require_POST
def actualizar_carrito(request, id):
    carrito = request.session.get('carrito', {})
    clave = str(id)

    try:
        cantidad = int(request.POST.get('cantidad', 1))
    except (TypeError, ValueError):
        messages.error(request, 'La cantidad no es válida.')
        return redirect('carrito')

    producto = Producto.objects.filter(id=id, activo=True).first()

    if cantidad <= 0 or producto is None:
        carrito.pop(clave, None)
    elif cantidad > producto.stock:
        carrito[clave] = producto.stock
        messages.warning(
            request,
            f'Solo quedan {producto.stock} disponibles de {producto.nombre}.'
        )
    else:
        carrito[clave] = cantidad

    if carrito.get(clave) == 0:
        carrito.pop(clave, None)

    _guardar_carrito(request, carrito)

    return redirect('carrito')
