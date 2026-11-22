from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from cuentas.models import Perfil
from tienda.models import Marca, Producto

from .models import Pedido
from .servicios import cancelar_pedido

User = get_user_model()

ENVIO = {
    'nombre': 'Ana López', 'telefono': '6681234567',
    'calle': 'Av. Las Flores 12', 'colonia': 'Centro',
    'ciudad': 'Los Mochis', 'estado_envio': 'Sinaloa',
    'codigo_postal': '81200', 'notas': '', 'guardar_en_perfil': 'on',
}


@override_settings(DESCUENTO_MAYORISTA='15')
class BaseTienda(TestCase):

    @classmethod
    def setUpTestData(cls):
        marca = Marca.objects.create(nombre='Lattafa', categoria=Marca.Categoria.ARABE)
        cls.khamrah = Producto.objects.create(
            nombre='Khamrah', marca=marca, descripcion='Dulce y especiado.',
            concentracion='EDP', genero='Unisex', volumen_ml=100,
            precio=Decimal('899.00'), stock=5,
        )
        cls.asad = Producto.objects.create(
            nombre='Asad', marca=marca, descripcion='Ámbar y pimienta.',
            concentracion='EDP', genero='Hombre', volumen_ml=100,
            precio=Decimal('650.00'), stock=1,
        )
        cls.cliente = User.objects.create_user('ana@x.com', 'ana@x.com', 'Clave#12345')
        cls.mayorista = User.objects.create_user('m@x.com', 'm@x.com', 'Clave#12345')
        Perfil.objects.filter(usuario=cls.mayorista).update(
            tipo=Perfil.Tipo.MAYORISTA, mayorista_aprobado=True,
        )

    def agregar(self, producto, veces=1):
        for _ in range(veces):
            self.client.post(reverse('agregar_carrito', args=[producto.id]))


class PrecioMayoristaTests(BaseTienda):

    def test_cliente_registrado_paga_precio_de_lista(self):
        self.client.force_login(self.cliente)
        r = self.client.get(self.khamrah.get_absolute_url())
        self.assertContains(r, '$899.00 MXN')
        self.assertNotContains(r, 'Mayorista -15%')

    def test_mayorista_aprobado_ve_15_por_ciento_menos(self):
        self.client.force_login(self.mayorista)
        r = self.client.get(self.khamrah.get_absolute_url())
        self.assertContains(r, '$764.15 MXN')  # 899 × 0.85
        self.assertContains(r, 'Mayorista -15%')

    def test_mayorista_pendiente_no_tiene_descuento(self):
        Perfil.objects.filter(usuario=self.mayorista).update(mayorista_aprobado=False)
        self.client.force_login(self.mayorista)
        r = self.client.get(self.khamrah.get_absolute_url())
        self.assertContains(r, '$899.00 MXN')


class CheckoutTests(BaseTienda):

    def test_checkout_pide_iniciar_sesion(self):
        self.agregar(self.khamrah)
        r = self.client.get(reverse('checkout'))
        self.assertRedirects(r, f"{reverse('entrar')}?next={reverse('checkout')}")

    def test_carrito_se_conserva_al_iniciar_sesion(self):
        self.agregar(self.khamrah, 2)
        self.client.post(reverse('entrar'), {'username': 'ana@x.com', 'password': 'Clave#12345'})
        r = self.client.get(reverse('checkout'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['totales']['total'], Decimal('1798.00'))

    def test_pedido_descuenta_stock_y_vacia_carrito(self):
        self.client.force_login(self.cliente)
        self.agregar(self.khamrah, 2)
        self.agregar(self.asad)

        r = self.client.post(reverse('checkout'), ENVIO)
        pedido = Pedido.objects.get()
        self.assertRedirects(r, pedido.get_absolute_url())

        self.assertEqual(pedido.total, Decimal('2448.00'))
        self.assertEqual(pedido.items.count(), 2)
        self.khamrah.refresh_from_db()
        self.asad.refresh_from_db()
        self.assertEqual(self.khamrah.stock, 3)
        self.assertEqual(self.asad.stock, 0)
        self.assertEqual(self.client.session['carrito'], {})
        self.assertEqual(self.cliente.perfil.__class__.objects.get(usuario=self.cliente).ciudad, 'Los Mochis')

    def test_pedido_de_mayorista_guarda_descuento(self):
        self.client.force_login(self.mayorista)
        self.agregar(self.khamrah, 2)
        self.client.post(reverse('checkout'), ENVIO)

        pedido = Pedido.objects.get()
        self.assertEqual(pedido.tipo_cliente, 'mayorista')
        self.assertEqual(pedido.subtotal, Decimal('1798.00'))
        self.assertEqual(pedido.total, Decimal('1528.30'))
        self.assertEqual(pedido.descuento, Decimal('269.70'))
        self.assertEqual(pedido.items.get().precio_unitario, Decimal('764.15'))

    def test_no_se_vende_mas_de_lo_que_hay(self):
        self.client.force_login(self.cliente)
        self.agregar(self.asad)
        # Otra compra se llevó la última pieza mientras el cliente llenaba el formulario.
        Producto.objects.filter(pk=self.asad.pk).update(stock=0)

        r = self.client.post(reverse('checkout'), ENVIO)
        self.assertRedirects(r, reverse('carrito'))
        self.assertFalse(Pedido.objects.exists())
        self.asad.refresh_from_db()
        self.assertEqual(self.asad.stock, 0)

    def test_carrito_vacio_regresa_al_carrito(self):
        self.client.force_login(self.cliente)
        self.assertRedirects(self.client.get(reverse('checkout')), reverse('carrito'))


class MisPedidosTests(BaseTienda):

    def crear_pedido(self, usuario):
        self.client.force_login(usuario)
        self.agregar(self.khamrah, 2)
        self.client.post(reverse('checkout'), ENVIO)
        return Pedido.objects.filter(usuario=usuario).latest('creado')

    def test_cliente_ve_sus_pedidos(self):
        pedido = self.crear_pedido(self.cliente)
        r = self.client.get(reverse('mis_pedidos'))
        self.assertContains(r, pedido.folio)

    def test_no_puede_ver_pedidos_ajenos(self):
        pedido = self.crear_pedido(self.cliente)
        self.client.force_login(self.mayorista)
        r = self.client.get(pedido.get_absolute_url())
        self.assertEqual(r.status_code, 404)

    def test_cancelar_regresa_stock_una_sola_vez(self):
        pedido = self.crear_pedido(self.cliente)
        self.khamrah.refresh_from_db()
        self.assertEqual(self.khamrah.stock, 3)

        self.assertTrue(cancelar_pedido(pedido))
        self.assertFalse(cancelar_pedido(pedido))
        self.khamrah.refresh_from_db()
        self.assertEqual(self.khamrah.stock, 5)

    def test_admin_cancelar_por_accion(self):
        pedido = self.crear_pedido(self.cliente)
        admin = User.objects.create_superuser('jefe', 'jefe@x.com', 'Clave#12345')
        self.client.force_login(admin)
        self.client.post(reverse('admin:pedidos_pedido_changelist'), {
            'action': 'cancelar', '_selected_action': [pedido.pk],
        })
        pedido.refresh_from_db()
        self.khamrah.refresh_from_db()
        self.assertEqual(pedido.estado, Pedido.Estado.CANCELADO)
        self.assertEqual(self.khamrah.stock, 5)
