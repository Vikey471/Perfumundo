from .models import Marca


def tienda(request):
    """Datos que necesitan todas las páginas: menú de categorías y carrito."""
    carrito = request.session.get('carrito', {})

    return {
        'categorias_menu': Marca.Categoria.choices,
        'carrito_cantidad': sum(carrito.values()),
    }
