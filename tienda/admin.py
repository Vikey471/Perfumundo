from django.contrib import admin

from .models import ImagenProducto, Marca, NotaOlfativa, Producto, ProductoNota


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'pais_origen')
    search_fields = ('nombre',)
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(NotaOlfativa)
class NotaOlfativaAdmin(admin.ModelAdmin):
    search_fields = ('nombre',)


class ProductoNotaInline(admin.TabularInline):
    model = ProductoNota
    extra = 3
    autocomplete_fields = ('nota',)


class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'marca',
        'concentracion',
        'volumen_ml',
        'genero',
        'precio',
        'stock',
        'destacado',
        'activo',
    )
    list_editable = ('precio', 'stock', 'destacado', 'activo')
    list_filter = (
        'genero',
        'concentracion',
        'marca',
        'destacado',
        'activo',
    )
    list_select_related = ('marca',)
    search_fields = (
        'nombre',
        'marca__nombre',
    )
    autocomplete_fields = ('marca',)
    prepopulated_fields = {'slug': ('nombre', 'concentracion', 'volumen_ml')}
    inlines = (ProductoNotaInline, ImagenProductoInline)
    fieldsets = (
        (None, {
            'fields': ('nombre', 'slug', 'marca', 'descripcion', 'imagen'),
        }),
        ('Ficha del perfume', {
            'fields': ('concentracion', 'genero', 'volumen_ml'),
        }),
        ('Venta', {
            'fields': ('precio', 'stock', 'destacado', 'activo'),
        }),
    )
