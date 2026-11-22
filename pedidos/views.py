from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from cuentas.models import Perfil
from tienda.carrito import Carrito

from .forms import DatosEnvioForm
from .models import Pedido
from .servicios import CarritoVacio, StockInsuficiente, crear_pedido


@login_required
def checkout(request):
    Perfil.objects.get_or_create(usuario=request.user)
    carrito = Carrito(request)
    lineas = carrito.lineas()

    if not lineas:
        messages.info(request, 'Tu carrito está vacío.')
        return redirect('carrito')

    if request.method == 'POST':
        form = DatosEnvioForm(request.POST)
        if form.is_valid():
            try:
                pedido = crear_pedido(request, form.datos_pedido())
            except StockInsuficiente as e:
                for producto, disponibles, pedidos in e.faltantes:
                    messages.warning(
                        request,
                        f'Solo quedan {disponibles} de {producto.nombre} '
                        f'(pediste {pedidos}). Ajusta tu carrito.'
                    )
                return redirect('carrito')
            except CarritoVacio:
                messages.info(request, 'Tu carrito está vacío.')
                return redirect('carrito')

            if form.cleaned_data.get('guardar_en_perfil'):
                form.guardar_en(request.user.perfil)

            messages.success(request, f'¡Gracias! Recibimos tu pedido {pedido.folio}.')
            return redirect(pedido)
    else:
        form = DatosEnvioForm.desde_perfil(request.user)

    return render(request, 'pedidos/checkout.html', {
        'form': form,
        'lineas': lineas,
        'totales': Carrito.totales(lineas),
    })


@login_required
def mis_pedidos(request):
    pedidos = (
        Pedido.objects
        .filter(usuario=request.user)
        .prefetch_related('items')
    )
    return render(request, 'pedidos/mis_pedidos.html', {'pedidos': pedidos})


@login_required
def detalle_pedido(request, pk):
    pedido = get_object_or_404(
        Pedido.objects.prefetch_related('items__producto'),
        pk=pk,
        usuario=request.user,
    )
    return render(request, 'pedidos/detalle_pedido.html', {'pedido': pedido})
