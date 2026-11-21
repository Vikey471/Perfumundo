"""Primer banner de ejemplo con la imagen del Dior Sauvage (si existe)."""
from django.db import migrations


def crear_banner_sauvage(apps, schema_editor):
    Banner = apps.get_model('tienda', 'Banner')
    Producto = apps.get_model('tienda', 'Producto')

    if Banner.objects.exists():
        return

    producto = (
        Producto.objects
        .filter(nombre__icontains='sauvage')
        .exclude(imagen='')
        .exclude(imagen__isnull=True)
        .first()
    )
    if producto is None:
        return

    Banner.objects.create(
        titulo='Dior Sauvage',
        subtitulo='Fresco, amaderado y magnético. Disponible en Perfumundo.',
        imagen=producto.imagen.name,  # reutiliza la misma foto del producto
        texto_boton='Ver perfume',
        producto=producto,
        orden=0,
        activo=True,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('tienda', '0007_banner'),
    ]

    operations = [
        migrations.RunPython(crear_banner_sauvage, migrations.RunPython.noop),
    ]
