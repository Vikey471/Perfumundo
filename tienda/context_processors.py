from pathlib import Path

from .carrito import CLAVE_SESION
from .models import Marca
from .precios import porcentaje_descuento


_ESTATICOS = [
    Path(__file__).resolve().parent / 'static' / 'tienda' / 'css' / 'estilos.css',
    Path(__file__).resolve().parent / 'static' / 'tienda' / 'js' / 'animaciones.js',
]


def _version_estaticos():
    """Cambia cada vez que se edita el CSS o el JS, para que el navegador
    no siga usando una copia vieja guardada en caché."""
    try:
        return int(max(p.stat().st_mtime for p in _ESTATICOS))
    except OSError:
        return 0


def tienda(request):
    """Datos que necesitan todas las páginas: menú, carrito y descuento."""
    carrito = request.session.get(CLAVE_SESION, {})

    return {
        'categorias_menu': Marca.Categoria.choices,
        'carrito_cantidad': sum(carrito.values()),
        'descuento_cliente': porcentaje_descuento(request.user),
        'version_estaticos': _version_estaticos(),
    }
