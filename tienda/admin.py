from django.contrib import admin

from django.utils.html import format_html

from .models import Banner, ImagenProducto, Marca, Producto


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


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('miniatura', 'titulo', 'producto', 'orden', 'activo')
    list_display_links = ('miniatura', 'titulo')
    list_editable = ('orden', 'activo')
    list_filter = ('activo',)
    list_select_related = ('producto',)
    autocomplete_fields = ('producto',)
    readonly_fields = ('vista_previa',)
    fields = (
        'titulo', 'subtitulo', 'imagen', 'vista_previa',
        'texto_boton', 'producto', 'enlace', 'orden', 'activo',
    )

    @admin.display(description='Imagen')
    def miniatura(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="height:60px;border-radius:4px">', obj.imagen.url)
        return '—'

    @admin.display(description='Vista previa')
    def vista_previa(self, obj):
        if obj and obj.imagen:
            return format_html('<img src="{}" style="max-height:260px;border-radius:6px">', obj.imagen.url)
        return 'Se mostrará al guardar.'
