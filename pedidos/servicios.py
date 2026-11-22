"""Operaciones de pedidos que tocan el inventario.

Todo lo que mueve stock pasa por aquí, dentro de transaction.atomic() y con
select_for_update() para que dos compras simultáneas no vendan la misma pieza.
"""
from django.db import transaction
from django.db.models import F

from tienda.carrito import Carrito
from tienda.models import Producto

from .models import Pedido, PedidoItem


class StockInsuficiente(Exception):
    def __init__(self, faltantes):
        self.faltantes = faltantes  # [(producto, disponibles, pedidos)]
        super().__init__('Stock insuficiente')


class CarritoVacio(Exception):
    pass


def crear_pedido(request, datos_envio):
    """Convierte el carrito de la sesión en un Pedido y descuenta el stock."""
    carrito = Carrito(request)
    ids = [int(i) for i in carrito.datos.keys()]
    if not ids:
        raise CarritoVacio()

    usuario = request.user
    perfil = usuario.perfil

    with transaction.atomic():
        # Bloquea las filas de los productos hasta terminar (orden por id
        # para evitar bloqueos cruzados entre compras simultáneas).
        productos = list(
            Producto.objects
            .select_for_update()
            .filter(id__in=ids, activo=True)
            .select_related('marca')
            .order_by('id')
        )
        lineas = carrito.lineas(productos)
        if not lineas:
            raise CarritoVacio()

        faltantes = [
            (l.producto, l.producto.stock, l.cantidad)
            for l in lineas if l.cantidad > l.producto.stock
        ]
        if faltantes:
            raise StockInsuficiente(faltantes)

        totales = Carrito.totales(lineas)
        pedido = Pedido.objects.create(
            usuario=usuario,
            tipo_cliente=perfil.tipo,
            descuento_porcentaje=carrito.porcentaje,
            subtotal=totales['subtotal'],
            descuento=totales['descuento'],
            total=totales['total'],
            **datos_envio,
        )

        PedidoItem.objects.bulk_create([
            PedidoItem(
                pedido=pedido,
                producto=l.producto,
                descripcion=str(l.producto),
                precio_lista=l.precio_lista,
                precio_unitario=l.precio_unitario,
                cantidad=l.cantidad,
            )
            for l in lineas
        ])

        for l in lineas:
            Producto.objects.filter(pk=l.producto.pk).update(
                stock=F('stock') - l.cantidad
            )

    carrito.vaciar()
    return pedido


def cancelar_pedido(pedido):
    """Cancela el pedido y regresa las piezas al inventario.

    Devuelve False si el pedido ya no se podía cancelar.
    """
    with transaction.atomic():
        pedido = Pedido.objects.select_for_update().get(pk=pedido.pk)
        if not pedido.cancelable:
            return False

        for item in pedido.items.all():
            Producto.objects.filter(pk=item.producto_id).update(
                stock=F('stock') + item.cantidad
            )

        pedido.estado = Pedido.Estado.CANCELADO
        pedido.save(update_fields=['estado', 'actualizado'])
    return True
