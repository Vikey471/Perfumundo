"""Carrito guardado en la sesión: {'<id producto>': cantidad}."""
from dataclasses import dataclass
from decimal import Decimal

from .models import Producto
from .precios import CERO, aplicar_descuento, porcentaje_descuento

CLAVE_SESION = 'carrito'


@dataclass
class LineaCarrito:
    producto: Producto
    cantidad: int
    precio_lista: Decimal
    precio_unitario: Decimal

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad

    @property
    def subtotal_lista(self):
        return self.precio_lista * self.cantidad


class Carrito:

    def __init__(self, request):
        self.request = request
        self.datos = request.session.get(CLAVE_SESION, {})
        self.porcentaje = porcentaje_descuento(request.user)

    def guardar(self):
        self.request.session[CLAVE_SESION] = self.datos
        self.request.session.modified = True

    def vaciar(self):
        self.datos = {}
        self.guardar()

    def __len__(self):
        return sum(self.datos.values())

    def lineas(self, productos=None):
        """Líneas del carrito con precios calculados.

        `productos` permite pasar un queryset ya bloqueado (checkout).
        """
        if productos is None:
            productos = Producto.objects.filter(
                id__in=self.datos.keys(), activo=True
            ).select_related('marca')

        lineas = []
        for producto in productos:
            cantidad = self.datos.get(str(producto.id), 0)
            if cantidad <= 0:
                continue
            lineas.append(LineaCarrito(
                producto=producto,
                cantidad=cantidad,
                precio_lista=producto.precio,
                precio_unitario=aplicar_descuento(producto.precio, self.porcentaje),
            ))
        return lineas

    @staticmethod
    def totales(lineas):
        subtotal = sum((l.subtotal_lista for l in lineas), CERO)
        total = sum((l.subtotal for l in lineas), CERO)
        return {
            'subtotal': subtotal,
            'descuento': subtotal - total,
            'total': total,
        }
