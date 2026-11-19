from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Perfil

User = get_user_model()

CLAVE = 'PerfumeSeguro#2026'


def datos_registro(**extra):
    datos = {
        'tipo': 'registrado',
        'first_name': 'Ana',
        'last_name': 'López',
        'email': 'Ana@Correo.com',
        'telefono': '',
        'empresa': '',
        'rfc': '',
        'password1': CLAVE,
        'password2': CLAVE,
    }
    datos.update(extra)
    return datos


class RegistroTests(TestCase):

    def test_registro_cliente_crea_usuario_perfil_y_sesion(self):
        r = self.client.post(reverse('registro'), datos_registro())
        self.assertRedirects(r, reverse('mi_cuenta'))

        usuario = User.objects.get(email='ana@correo.com')
        self.assertEqual(usuario.username, 'ana@correo.com')
        self.assertEqual(usuario.perfil.tipo, Perfil.Tipo.REGISTRADO)
        self.assertEqual(int(self.client.session['_auth_user_id']), usuario.pk)

    def test_mayorista_requiere_empresa_y_telefono(self):
        r = self.client.post(reverse('registro'), datos_registro(tipo='mayorista'))
        self.assertEqual(r.status_code, 200)
        self.assertIn('empresa', r.context['form'].errors)
        self.assertIn('telefono', r.context['form'].errors)
        self.assertFalse(User.objects.exists())

    def test_mayorista_queda_pendiente_de_aprobacion(self):
        self.client.post(reverse('registro'), datos_registro(
            tipo='mayorista', empresa='Perfumes del Valle',
            telefono='6681234567', rfc='pdv010101ab1',
        ))
        perfil = Perfil.objects.get(usuario__email='ana@correo.com')
        self.assertTrue(perfil.mayorista_pendiente)
        self.assertFalse(perfil.es_mayorista)
        self.assertEqual(perfil.rfc, 'PDV010101AB1')

    def test_correo_repetido_no_se_registra(self):
        self.client.post(reverse('registro'), datos_registro())
        self.client.logout()
        r = self.client.post(reverse('registro'), datos_registro(email='ANA@correo.com'))
        self.assertIn('email', r.context['form'].errors)
        self.assertEqual(User.objects.count(), 1)


class EntrarYCuentaTests(TestCase):

    def setUp(self):
        self.client.post(reverse('registro'), datos_registro())
        self.client.logout()

    def test_entrar_con_correo_sin_importar_mayusculas(self):
        r = self.client.post(reverse('entrar'), {
            'username': 'ANA@correo.com', 'password': CLAVE,
        })
        self.assertRedirects(r, reverse('mi_cuenta'))

    def test_mi_cuenta_pide_iniciar_sesion(self):
        r = self.client.get(reverse('mi_cuenta'))
        self.assertRedirects(r, f"{reverse('entrar')}?next={reverse('mi_cuenta')}")

    def test_guardar_direccion(self):
        self.client.login(username='ana@correo.com', password=CLAVE)
        r = self.client.post(reverse('mi_cuenta'), {
            'first_name': 'Ana', 'last_name': 'López', 'telefono': '6681234567',
            'calle': 'Av. Las Flores 12', 'colonia': 'Centro',
            'ciudad': 'Los Mochis', 'estado': 'Sinaloa', 'codigo_postal': '81200',
        })
        self.assertRedirects(r, reverse('mi_cuenta'))
        self.assertEqual(Perfil.objects.get().ciudad, 'Los Mochis')

    def test_codigo_postal_invalido(self):
        self.client.login(username='ana@correo.com', password=CLAVE)
        r = self.client.post(reverse('mi_cuenta'), {
            'first_name': 'Ana', 'last_name': 'López', 'codigo_postal': '12ab',
        })
        self.assertIn('codigo_postal', r.context['perfil_form'].errors)

    def test_salir_solo_por_post(self):
        self.client.login(username='ana@correo.com', password=CLAVE)
        self.assertEqual(self.client.get(reverse('salir')).status_code, 405)
        r = self.client.post(reverse('salir'))
        self.assertRedirects(r, reverse('inicio'))


class AdminTests(TestCase):

    def test_accion_aprobar_mayoristas(self):
        admin = User.objects.create_superuser('jefe', 'jefe@x.com', CLAVE)
        cliente = User.objects.create_user('m@x.com', 'm@x.com', CLAVE)
        cliente.perfil.tipo = Perfil.Tipo.MAYORISTA
        cliente.perfil.save()

        self.client.force_login(admin)
        self.client.post(reverse('admin:cuentas_perfil_changelist'), {
            'action': 'aprobar_mayoristas',
            '_selected_action': [cliente.perfil.pk],
        })
        cliente.perfil.refresh_from_db()
        self.assertTrue(cliente.perfil.es_mayorista)
