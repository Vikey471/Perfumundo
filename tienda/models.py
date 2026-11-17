from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


def _slug_unico(instancia, texto):
    """Genera un slug a partir de `texto` que no choque con otro registro."""
    base = slugify(texto)[:200] or 'item'
    slug = base
    modelo = type(instancia)
    n = 2
    while modelo.objects.filter(slug=slug).exclude(pk=instancia.pk).exists():
        slug = f'{base}-{n}'
        n += 1
    return slug


class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    pais_origen = models.CharField(max_length=60, blank=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'marca'
        verbose_name_plural = 'marcas'

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _slug_unico(self, self.nombre)
        super().save(*args, **kwargs)


class NotaOlfativa(models.Model):
    nombre = models.CharField(max_length=60, unique=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'nota olfativa'
        verbose_name_plural = 'notas olfativas'

    def __str__(self):
        return self.nombre


class Producto(models.Model):

    class Genero(models.TextChoices):
        HOMBRE = 'Hombre', 'Hombre'
        MUJER = 'Mujer', 'Mujer'
        UNISEX = 'Unisex', 'Unisex'

    class Concentracion(models.TextChoices):
        EDC = 'EDC', 'Eau de Cologne'
        EDT = 'EDT', 'Eau de Toilette'
        EDP = 'EDP', 'Eau de Parfum'
        PARFUM = 'PARFUM', 'Parfum / Extrait'

    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    marca = models.ForeignKey(
        Marca,
        on_delete=models.PROTECT,
        related_name='productos'
    )
    descripcion = models.TextField()

    concentracion = models.CharField(
        max_length=10,
        choices=Concentracion.choices,
        default=Concentracion.EDP
    )
    genero = models.CharField(max_length=20, choices=Genero.choices)
    volumen_ml = models.PositiveSmallIntegerField(
        'volumen (ml)',
        validators=[MinValueValidator(1)]
    )

    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    stock = models.PositiveIntegerField(default=0)

    notas = models.ManyToManyField(
        NotaOlfativa,
        through='ProductoNota',
        related_name='productos',
        blank=True
    )

    imagen = models.ImageField(
        'imagen principal',
        upload_to='productos/',
        blank=True,
        null=True
    )

    destacado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['marca__nombre', 'nombre', 'volumen_ml']
        indexes = [
            models.Index(fields=['activo', 'genero'], name='tienda_prod_activo_genero_idx'),
            models.Index(fields=['activo', 'destacado'], name='tienda_prod_activo_destac_idx'),
        ]

    def __str__(self):
        return f'{self.marca} {self.nombre} {self.get_concentracion_display()} {self.volumen_ml} ml'

    def save(self, *args, **kwargs):
        if not self.slug:
            nombre = self.nombre
            if not nombre.lower().startswith(self.marca.nombre.lower()):
                nombre = f'{self.marca.nombre} {nombre}'
            self.slug = _slug_unico(
                self,
                f'{nombre} {self.concentracion} {self.volumen_ml}ml'
            )
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('detalle_producto', args=[self.slug])

    @property
    def disponible(self):
        return self.activo and self.stock > 0

    def notas_por_tipo(self):
        """Devuelve {'Salida': [...], 'Corazón': [...], 'Fondo': [...]}."""
        grupos = {etiqueta: [] for _, etiqueta in ProductoNota.Tipo.choices}
        for pn in self.producto_notas.all():
            grupos[pn.get_tipo_display()].append(pn.nota.nombre)
        return {k: v for k, v in grupos.items() if v}


class ProductoNota(models.Model):

    class Tipo(models.TextChoices):
        SALIDA = 'salida', 'Salida'
        CORAZON = 'corazon', 'Corazón'
        FONDO = 'fondo', 'Fondo'

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='producto_notas'
    )
    nota = models.ForeignKey(NotaOlfativa, on_delete=models.PROTECT)
    tipo = models.CharField(max_length=10, choices=Tipo.choices)

    class Meta:
        verbose_name = 'nota del producto'
        verbose_name_plural = 'notas del producto'
        constraints = [
            models.UniqueConstraint(
                fields=['producto', 'nota', 'tipo'],
                name='nota_unica_por_tipo'
            ),
        ]

    def __str__(self):
        return f'{self.nota} ({self.get_tipo_display()})'


class ImagenProducto(models.Model):
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='imagenes'
    )
    imagen = models.ImageField(upload_to='productos/galeria/')
    texto_alternativo = models.CharField(max_length=150, blank=True)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['orden', 'id']
        verbose_name = 'imagen del producto'
        verbose_name_plural = 'galería de imágenes'

    def __str__(self):
        return f'Imagen {self.orden} de {self.producto.nombre}'
