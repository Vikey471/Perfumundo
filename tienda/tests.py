from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Marca, Producto


class CatalogoTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        lattafa = Marca.objects.create(nombre='Lattafa', categoria=Marca.Categoria.ARABE)
        dior = Marca.objects.create(nombre='Dior', categoria=Marca.Categoria.DISENADOR)
        comun = dict(descripcion='Prueba.', concentracion='EDP', genero='Hombre',
                     volumen_ml=100, precio=Decimal('900.00'), stock=3)
        cls.khamrah = Producto.objects.create(nombre='Khamrah', marca=lattafa, destacado=True, **comun)
        cls.sauvage = Producto.objects.create(
            nombre='Sauvage', marca=dior, liquidacion=True,
            detalle_liquidacion='Parcial 70/100 ml', **comun,
        )

    def test_seccion_liquidacion_solo_muestra_productos_marcados(self):
        r = self.client.get(reverse('catalogo'), {'categoria': 'liquidacion'})
        self.assertEqual(list(r.context['productos']), [self.sauvage])
        self.assertContains(r, 'Parcial 70/100 ml')

    def test_producto_en_liquidacion_sigue_en_su_categoria(self):
        r = self.client.get(reverse('catalogo'), {'categoria': 'disenador'})
        self.assertIn(self.sauvage, r.context['productos'])

    def test_categoria_arabe(self):
        r = self.client.get(reverse('catalogo'), {'categoria': 'arabe'})
        self.assertEqual(list(r.context['productos']), [self.khamrah])

    def test_menu_incluye_liquidacion(self):
        r = self.client.get(reverse('inicio'))
        self.assertContains(r, '?categoria=liquidacion')

    def test_portada_destacados_antes_que_ofertas(self):
        html = self.client.get(reverse('inicio')).content.decode()
        self.assertLess(html.index('Productos destacados'), html.index('Ofertas de la semana'))
        self.assertLess(html.index('Ofertas de la semana'), html.index('Explora nuestras categorías'))

    def test_detalle_muestra_aviso_de_liquidacion(self):
        r = self.client.get(self.sauvage.get_absolute_url())
        self.assertContains(r, 'liquidation-note')


class BannerTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        from .models import Banner
        dior = Marca.objects.create(nombre='Dior', categoria=Marca.Categoria.DISENADOR)
        cls.sauvage = Producto.objects.create(
            nombre='Sauvage', marca=dior, descripcion='Prueba.', concentracion='EDT',
            genero='Hombre', volumen_ml=200, precio=Decimal('2300.00'), stock=1,
        )
        cls.Banner = Banner

    def test_sin_banners_muestra_logo(self):
        r = self.client.get(reverse('inicio'))
        self.assertContains(r, 'banner-empty')
        self.assertNotContains(r, 'data-carousel')

    def test_banners_activos_en_orden_y_enlace_al_producto(self):
        self.Banner.objects.create(titulo='Segundo', imagen='banners/b.jpg', orden=2, enlace='/catalogo/?categoria=arabe')
        self.Banner.objects.create(titulo='Primero', imagen='banners/a.jpg', orden=1, producto=self.sauvage)
        self.Banner.objects.create(titulo='Oculto', imagen='banners/c.jpg', orden=0, activo=False)

        r = self.client.get(reverse('inicio'))
        html = r.content.decode()
        self.assertContains(r, 'data-carousel')
        self.assertNotContains(r, 'Oculto')
        self.assertLess(html.index('Primero'), html.index('Segundo'))
        self.assertContains(r, self.sauvage.get_absolute_url())
        self.assertContains(r, '<figure class="banner-slide', count=2)
        self.assertNotContains(r, 'banner-dot')
