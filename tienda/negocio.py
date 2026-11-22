"""Datos fijos del negocio que se muestran en la página (contacto y ubicación).

Si cambia la dirección, el horario o las redes, se edita solo aquí.
"""
from urllib.parse import quote

NOMBRE = 'Perfumundo LM'

DIRECCION_CALLE = 'Av. Agustina Ramírez 2051'
DIRECCION_COLONIA = 'Álamos Country'
DIRECCION_CIUDAD = '81271 Los Mochis, Sin.'
DIRECCION_COMPLETA = f'{DIRECCION_CALLE}, {DIRECCION_COLONIA}, {DIRECCION_CIUDAD}'

HORARIO = [
    ('Lunes a sábado', '10:00 a.m. – 8:00 p.m.'),
    ('Domingo', 'Cerrado'),
]

WHATSAPP = '526681303333'
WHATSAPP_VISIBLE = '668 130 3333'
INSTAGRAM_URL = 'https://www.instagram.com/perfumundolm'
FACEBOOK_URL = 'https://www.facebook.com/share/1Kw95ZjjS5/'

MAPS_URL = 'https://maps.app.goo.gl/XJk6ZV32aoRGsXZT6'
_BUSQUEDA = quote(f'{NOMBRE}, {DIRECCION_COMPLETA}')
MAPS_EMBED_URL = f'https://www.google.com/maps?q={_BUSQUEDA}&z=16&output=embed'
WAZE_URL = f'https://waze.com/ul?q={_BUSQUEDA}&navigate=yes'


def contexto():
    return {
        'nombre': NOMBRE,
        'calle': DIRECCION_CALLE,
        'colonia': DIRECCION_COLONIA,
        'ciudad': DIRECCION_CIUDAD,
        'direccion': DIRECCION_COMPLETA,
        'horario': HORARIO,
        'whatsapp': WHATSAPP,
        'whatsapp_visible': WHATSAPP_VISIBLE,
        'instagram_url': INSTAGRAM_URL,
        'facebook_url': FACEBOOK_URL,
        'maps_url': MAPS_URL,
        'maps_embed_url': MAPS_EMBED_URL,
        'waze_url': WAZE_URL,
    }
