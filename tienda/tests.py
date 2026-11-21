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
