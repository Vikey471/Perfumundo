from django.conf import settings
from django.db import models


class Perfil(models.Model):
    """Datos de cliente ligados al usuario de Django.

    Los administradores no necesitan perfil de cliente: usan el admin.
    """

    class Tipo(models.TextChoices):
        REGISTRADO = 'registrado', 'Cliente registrado'
        MAYORISTA = 'mayorista', 'Cliente mayorista'

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil'
    )
    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices,
        default=Tipo.REGISTRADO
    )
    telefono = models.CharField('teléfono', max_length=20, blank=True)

    # Solo para mayoristas
    empresa = models.CharField('empresa o negocio', max_length=150, blank=True)
    rfc = models.CharField('RFC', max_length=13, blank=True)
    mayorista_aprobado = models.BooleanField(
        default=False,
        help_text='Márcalo cuando hayas validado al cliente mayorista.'
    )

    # Dirección de envío
    calle = models.CharField('calle y número', max_length=200, blank=True)
    colonia = models.CharField(max_length=100, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=100, blank=True)
    codigo_postal = models.CharField('código postal', max_length=5, blank=True)

    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'perfil de cliente'
        verbose_name_plural = 'perfiles de cliente'

    def __str__(self):
        nombre = self.usuario.get_full_name() or self.usuario.email or self.usuario.username
        return f'{nombre} ({self.get_tipo_display()})'

    @property
    def es_mayorista(self):
        """Mayorista ya validado por el administrador."""
        return self.tipo == self.Tipo.MAYORISTA and self.mayorista_aprobado

    @property
    def mayorista_pendiente(self):
        return self.tipo == self.Tipo.MAYORISTA and not self.mayorista_aprobado
