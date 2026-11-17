from django.db import models


class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    marca = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    categoria = models.CharField(
        max_length=20,
        choices=[
            ('Hombre', 'Hombre'),
            ('Mujer', 'Mujer'),
            ('Unisex', 'Unisex'),
        ]
    )

    imagen = models.ImageField(
        upload_to='productos/',
        blank=True,
        null=True
    )

    destacado = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre