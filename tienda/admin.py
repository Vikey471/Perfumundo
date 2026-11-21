from django.contrib import admin

from .models import ImagenProducto, Marca, Producto


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'pais_origen')
    list_filter = ('categoria',)
    search_fields = ('nombre',)
    prepopulated_fields = {'slug': ('nombre',)}


class ImagenProductoInline(admin.TabularInline):
    model = ImagenProducto
    extra = 1


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        'nombre',
        'marca',
        'categoria',
        'concentracion',
        'volumen_ml',
        'genero',
        'precio',
        'stock',
        'destacado',
        'liquidacion',
        'activo',
    )
    list_editable = ('precio', 'stock', 'destacado', 'liquidacion', 'activo')
    list_filter = (
        'marca__categoria',
        'genero',
        'concentracion',
        'marca',
        'destacado',
        'liquidacion',
        'activo',
    )
    list_select_related = ('marca',)
    search_fields = (
        'nombre',
        'marca__nombre',
    )
    autocomplete_fields = ('marca',)
    prepopulated_fields = {'slug': ('nombre', 'concentracion', 'volumen_ml')}
    inlines = (ImagenProductoInline,)

    @admin.display(description='Categoría', ordering='marca__categoria')
    def categoria(self, obj):
        return obj.marca.get_categoria_display()

    fieldsets = (
        (None, {
            'fields': ('nombre', 'slug', 'marca', 'descripcion', 'url_fragrantica', 'imagen'),
        }),
        ('Ficha del perfume', {
            'fields': ('concentracion', 'genero', 'volumen_ml'),
        }),
        ('Venta', {
            'fields': ('precio', 'stock', 'destacado', 'activo'),
        }),
        ('Liquidación y parciales', {
            'fields': ('liquidacion', 'detalle_liquidacion'),
        }),
    )
