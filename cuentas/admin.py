from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Perfil

User = get_user_model()


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = (
        'nombre', 'correo', 'tipo', 'mayorista_aprobado',
        'empresa', 'telefono', 'fecha_registro',
    )
    list_filter = ('tipo', 'mayorista_aprobado')
    list_select_related = ('usuario',)
    search_fields = (
        'usuario__first_name', 'usuario__last_name', 'usuario__email',
        'empresa', 'rfc', 'telefono',
    )
    readonly_fields = ('usuario', 'fecha_registro')
    actions = ('aprobar_mayoristas',)
    fieldsets = (
        (None, {'fields': ('usuario', 'tipo', 'telefono', 'fecha_registro')}),
        ('Mayorista', {'fields': ('empresa', 'rfc', 'mayorista_aprobado')}),
        ('Dirección de envío', {
            'fields': ('calle', 'colonia', 'ciudad', 'estado', 'codigo_postal'),
        }),
    )

    @admin.display(description='Nombre', ordering='usuario__first_name')
    def nombre(self, obj):
        return obj.usuario.get_full_name() or obj.usuario.username

    @admin.display(description='Correo', ordering='usuario__email')
    def correo(self, obj):
        return obj.usuario.email

    @admin.action(description='Aprobar mayoristas seleccionados')
    def aprobar_mayoristas(self, request, queryset):
        n = queryset.filter(tipo=Perfil.Tipo.MAYORISTA).update(mayorista_aprobado=True)
        self.message_user(request, f'{n} mayorista(s) aprobado(s).', messages.SUCCESS)


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    extra = 0


admin.site.unregister(User)


@admin.register(User)
class UsuarioAdmin(UserAdmin):
    inlines = (PerfilInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
