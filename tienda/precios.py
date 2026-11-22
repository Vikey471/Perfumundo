"""Reglas de precio de la tienda.

Los mayoristas aprobados reciben un descuento general sobre el precio de
lista. El porcentaje se configura con DESCUENTO_MAYORISTA en el .env.
"""
from decimal import ROUND_HALF_UP, Decimal

from django.conf import settings

CERO = Decimal('0')
CENTAVO = Decimal('0.01')


def porcentaje_descuento(usuario):
    """Porcentaje de descuento que le toca a este usuario (0 si no aplica)."""
    if not getattr(usuario, 'is_authenticated', False):
        return CERO
    perfil = getattr(usuario, 'perfil', None)
    if perfil is not None and perfil.es_mayorista:
        return Decimal(settings.DESCUENTO_MAYORISTA)
    return CERO


def aplicar_descuento(precio, porcentaje):
    """Precio con el descuento aplicado, redondeado a centavos."""
    if not porcentaje:
        return precio
    factor = (Decimal('100') - Decimal(porcentaje)) / Decimal('100')
    return (Decimal(precio) * factor).quantize(CENTAVO, rounding=ROUND_HALF_UP)
