from .carrito import CLAVE_SESION
from .models import Marca
from .precios import porcentaje_descuento


def tienda(request):
    """Datos que necesitan todas las páginas: menú, carrito y descuento."""
    carrito = request.session.get(CLAVE_SESION, {})

    return {
        'categorias_menu': Marca.Categoria.choices,
        'carrito_cantidad': sum(carrito.values()),
        'descuento_cliente': porcentaje_descuento(request.user),
    }
