from django import template

from ..precios import aplicar_descuento

register = template.Library()


@register.filter
def con_descuento(precio, porcentaje):
    """{{ producto.precio|con_descuento:descuento_cliente }}"""
    return aplicar_descuento(precio, porcentaje)


@register.inclusion_tag('tienda/_precio.html', takes_context=True)
def precio_producto(context, producto, clase='product-price'):
    porcentaje = context.get('descuento_cliente') or 0
    return {
        'precio_lista': producto.precio,
        'precio_final': aplicar_descuento(producto.precio, porcentaje),
        'porcentaje': porcentaje,
        'clase': clase,
    }
