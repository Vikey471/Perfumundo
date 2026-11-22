"""
Catálogo detallado: Marca como modelo, notas olfativas, concentración,
volumen, galería de imágenes, slug y `categoria` renombrada a `genero`.

Conserva los productos existentes: crea una Marca por cada texto de marca
distinto y genera el slug de cada producto.
"""
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models
from django.utils.text import slugify


def _slug_unico(modelo, texto, pk=None):
    base = slugify(texto)[:200] or 'item'
    slug, n = base, 2
    while modelo.objects.filter(slug=slug).exclude(pk=pk).exists():
        slug = f'{base}-{n}'
        n += 1
    return slug


def pasar_marcas_y_slugs(apps, schema_editor):
    Marca = apps.get_model('tienda', 'Marca')
    Producto = apps.get_model('tienda', 'Producto')

    for producto in Producto.objects.all():
        nombre_marca = (producto.marca_texto or 'Sin marca').strip()
        marca = Marca.objects.filter(nombre__iexact=nombre_marca).first()
        if marca is None:
            marca = Marca.objects.create(
                nombre=nombre_marca,
                slug=_slug_unico(Marca, nombre_marca),
            )
        producto.marca = marca
        producto.slug = _slug_unico(
            Producto,
            f'{marca.nombre} {producto.nombre} {producto.concentracion} {producto.volumen_ml}ml',
            pk=producto.pk,
        )
        producto.save(update_fields=['marca', 'slug'])


def regresar_marcas(apps, schema_editor):
    Producto = apps.get_model('tienda', 'Producto')
    for producto in Producto.objects.select_related('marca'):
        producto.marca_texto = producto.marca.nombre
        producto.save(update_fields=['marca_texto'])


class Migration(migrations.Migration):

    dependencies = [
        ('tienda', '0002_alter_producto_categoria'),
    ]

    operations = [
        # --- Modelos nuevos de catálogo ---
        migrations.CreateModel(
            name='Marca',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=120, unique=True)),
                ('pais_origen', models.CharField(blank=True, max_length=60)),
                ('descripcion', models.TextField(blank=True)),
            ],
            options={'verbose_name': 'marca', 'verbose_name_plural': 'marcas', 'ordering': ['nombre']},
        ),
        migrations.CreateModel(
            name='NotaOlfativa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=60, unique=True)),
            ],
            options={'verbose_name': 'nota olfativa', 'verbose_name_plural': 'notas olfativas', 'ordering': ['nombre']},
        ),

        # --- categoria -> genero ---
        migrations.RenameField(model_name='producto', old_name='categoria', new_name='genero'),
        migrations.AlterField(
            model_name='producto',
            name='genero',
            field=models.CharField(choices=[('Hombre', 'Hombre'), ('Mujer', 'Mujer'), ('Unisex', 'Unisex')], max_length=20),
        ),

        # --- Campos nuevos (con valores por defecto para productos existentes) ---
        migrations.AddField(
            model_name='producto',
            name='concentracion',
            field=models.CharField(choices=[('EDC', 'Eau de Cologne'), ('EDT', 'Eau de Toilette'), ('EDP', 'Eau de Parfum'), ('PARFUM', 'Parfum / Extrait')], default='EDP', max_length=10),
        ),
        migrations.AddField(
            model_name='producto',
            name='volumen_ml',
            field=models.PositiveSmallIntegerField(default=100, validators=[django.core.validators.MinValueValidator(1)], verbose_name='volumen (ml)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='producto',
            name='fecha_actualizacion',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='producto',
            name='slug',
            field=models.SlugField(blank=True, max_length=220, null=True, db_index=False),
        ),

        # --- marca (texto) -> marca (FK a Marca) ---
        migrations.RenameField(model_name='producto', old_name='marca', new_name='marca_texto'),
        migrations.AddField(
            model_name='producto',
            name='marca',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='productos', to='tienda.marca'),
        ),
        migrations.RunPython(pasar_marcas_y_slugs, regresar_marcas),
        migrations.RemoveField(model_name='producto', name='marca_texto'),
        migrations.AlterField(
            model_name='producto',
            name='marca',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='productos', to='tienda.marca'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='slug',
            field=models.SlugField(blank=True, max_length=220, unique=True),
        ),

        # --- Ajustes de campos existentes ---
        migrations.AlterField(
            model_name='producto',
            name='precio',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='producto',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='productos/', verbose_name='imagen principal'),
        ),

        # --- Notas por producto y galería ---
        migrations.CreateModel(
            name='ProductoNota',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('salida', 'Salida'), ('corazon', 'Corazón'), ('fondo', 'Fondo')], max_length=10)),
                ('nota', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='tienda.notaolfativa')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='producto_notas', to='tienda.producto')),
            ],
            options={'verbose_name': 'nota del producto', 'verbose_name_plural': 'notas del producto'},
        ),
        migrations.AddConstraint(
            model_name='productonota',
            constraint=models.UniqueConstraint(fields=('producto', 'nota', 'tipo'), name='nota_unica_por_tipo'),
        ),
        migrations.AddField(
            model_name='producto',
            name='notas',
            field=models.ManyToManyField(blank=True, related_name='productos', through='tienda.ProductoNota', to='tienda.notaolfativa'),
        ),
        migrations.CreateModel(
            name='ImagenProducto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagen', models.ImageField(upload_to='productos/galeria/')),
                ('texto_alternativo', models.CharField(blank=True, max_length=150)),
                ('orden', models.PositiveSmallIntegerField(default=0)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='imagenes', to='tienda.producto')),
            ],
            options={'verbose_name': 'imagen del producto', 'verbose_name_plural': 'galería de imágenes', 'ordering': ['orden', 'id']},
        ),

        # --- Orden e índices ---
        migrations.AlterModelOptions(
            name='producto',
            options={'ordering': ['marca__nombre', 'nombre', 'volumen_ml']},
        ),
        migrations.AddIndex(
            model_name='producto',
            index=models.Index(fields=['activo', 'genero'], name='tienda_prod_activo_genero_idx'),
        ),
        migrations.AddIndex(
            model_name='producto',
            index=models.Index(fields=['activo', 'destacado'], name='tienda_prod_activo_destac_idx'),
        ),
    ]
