from django.contrib import admin, messages

from .models import Pedido, PedidoItem
from .servicios import cancelar_pedido


class PedidoItemInline(admin.TabularInline):
    model = PedidoItem
    extra = 0
    can_delete = False
    fields = ('producto', 'descripcion', 'cantidad', 'precio_lista', 'precio_unitario', 'subtotal')
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description='Subtotal')
    def subtotal(self, obj):
        return obj.subtotal


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('folio', 'cliente', 'tipo_cliente', 'estado', 'total', 'creado')
    list_filter = ('estado', 'tipo_cliente', 'creado')
    list_select_related = ('usuario',)
    search_fields = ('id', 'usuario__email', 'nombre', 'telefono')
    date_hierarchy = 'creado'
    inlines = (PedidoItemInline,)
    actions = ('marcar_pagado', 'marcar_enviado', 'marcar_entregado', 'cancelar')
    readonly_fields = (
        'folio', 'usuario', 'tipo_cliente', 'descuento_porcentaje',
        'subtotal', 'descuento', 'total', 'creado', 'actualizado',
    )
    fieldsets = (
        (None, {'fields': ('folio', 'usuario', 'estado', 'creado', 'actualizado')}),
        ('Importes', {
            'fields': ('tipo_cliente', 'descuento_porcentaje', 'subtotal', 'descuento', 'total'),
        }),
        ('Envío', {
            'fields': (
                'nombre', 'telefono', 'calle', 'colonia', 'ciudad',
                'estado_envio', 'codigo_postal', 'notas',
            ),
        }),
    )

    def has_add_permission(self, request):
        # Los pedidos nacen en la tienda, no en el admin.
        return False

    def get_readonly_fields(self, request, obj=None):
        campos = list(super().get_readonly_fields(request, obj))
        # Cancelar desde el campo "estado" no regresaría el stock: se usa la acción.
        if obj and obj.estado == Pedido.Estado.CANCELADO:
            campos.append('estado')
        return campos

    def save_model(self, request, obj, form, change):
        if change and 'estado' in form.changed_data and obj.estado == Pedido.Estado.CANCELADO:
            estado_anterior = form.initial.get('estado')
            obj.estado = estado_anterior
            super().save_model(request, obj, form, change)
            if cancelar_pedido(obj):
                obj.estado = Pedido.Estado.CANCELADO
                self.message_user(request, 'Pedido cancelado y stock regresado.', messages.SUCCESS)
            else:
                self.message_user(request, 'Este pedido ya no se puede cancelar.', messages.ERROR)
            return
        super().save_model(request, obj, form, change)

    @admin.display(description='Cliente', ordering='usuario__email')
    def cliente(self, obj):
        return obj.usuario.get_full_name() or obj.usuario.email

    def _cambiar_estado(self, request, queryset, estado):
        n = queryset.exclude(estado=Pedido.Estado.CANCELADO).update(estado=estado)
        self.message_user(request, f'{n} pedido(s) actualizado(s).', messages.SUCCESS)

    @admin.action(description='Marcar como pagado')
    def marcar_pagado(self, request, queryset):
        self._cambiar_estado(request, queryset, Pedido.Estado.PAGADO)

    @admin.action(description='Marcar como enviado')
    def marcar_enviado(self, request, queryset):
        self._cambiar_estado(request, queryset, Pedido.Estado.ENVIADO)

    @admin.action(description='Marcar como entregado')
    def marcar_entregado(self, request, queryset):
        self._cambiar_estado(request, queryset, Pedido.Estado.ENTREGADO)

    @admin.action(description='Cancelar y regresar stock')
    def cancelar(self, request, queryset):
        ok = sum(1 for pedido in queryset if cancelar_pedido(pedido))
        omitidos = queryset.count() - ok
        self.message_user(request, f'{ok} pedido(s) cancelado(s); stock regresado.', messages.SUCCESS)
        if omitidos:
            self.message_user(
                request,
                f'{omitidos} pedido(s) no se cancelaron porque ya estaban enviados, entregados o cancelados.',
                messages.WARNING,
            )
