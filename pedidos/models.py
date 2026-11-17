from decimal import Decimal

from django.conf import settings
from django.db import models
from django.urls import reverse

from tienda.models import Producto


class Pedido(models.Model):

    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente de pago'
        PAGADO = 'pagado', 'Pagado'
        ENVIADO = 'enviado', 'Enviado'
        ENTREGADO = 'entregado', 'Entregado'
        CANCELADO = 'cancelado', 'Cancelado'

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='pedidos'
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        db_index=True
    )

    # Condiciones del cliente al momento de comprar
    tipo_cliente = models.CharField(max_length=20)
    descuento_porcentaje = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('0')
    )

    # Totales congelados
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    total = models.DecimalField(max_digits=12, decimal_places=2)

    # Datos de envío (copia: no cambian si el cliente edita su perfil)
    nombre = models.CharField('nombre de quien recibe', max_length=200)
    telefono = models.CharField('teléfono', max_length=20)
    calle = models.CharField('calle y número', max_length=200)
    colonia = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    estado_envio = models.CharField('estado', max_length=100)
    codigo_postal = models.CharField('código postal', max_length=5)
    notas = models.TextField('notas para la entrega', blank=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-creado']
        verbose_name = 'pedido'
        verbose_name_plural = 'pedidos'

    def __str__(self):
        return f'Pedido {self.folio}'

    @property
    def folio(self):
        return f'PM-{self.pk:05d}' if self.pk else 'PM-nuevo'

    def get_absolute_url(self):
        return reverse('detalle_pedido', args=[self.pk])

    @property
    def cancelable(self):
        return self.estado in (self.Estado.PENDIENTE, self.Estado.PAGADO)


class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='pedido_items'
    )
    # Copia del producto al momento de la compra
    descripcion = models.CharField(max_length=300)
    precio_lista = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'producto del pedido'
        verbose_name_plural = 'productos del pedido'

    def __str__(self):
        return f'{self.cantidad} × {self.descripcion}'

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad
