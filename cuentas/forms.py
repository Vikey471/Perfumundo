from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Perfil

User = get_user_model()


class RegistroForm(UserCreationForm):
    first_name = forms.CharField(label='Nombre', max_length=150)
    last_name = forms.CharField(label='Apellidos', max_length=150)
    email = forms.EmailField(label='Correo electrónico')
    tipo = forms.ChoiceField(
        label='Tipo de cliente',
        choices=Perfil.Tipo.choices,
        widget=forms.RadioSelect,
        initial=Perfil.Tipo.REGISTRADO,
    )
    telefono = forms.CharField(label='Teléfono', max_length=20, required=False)
    empresa = forms.CharField(label='Empresa o negocio', max_length=150, required=False)
    rfc = forms.CharField(label='RFC (opcional)', max_length=13, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        existe = (
            User.objects.filter(email__iexact=email).exists()
            or User.objects.filter(username__iexact=email).exists()
        )
        if existe:
            raise forms.ValidationError('Ya existe una cuenta con este correo.')
        return email

    def clean_rfc(self):
        return self.cleaned_data.get('rfc', '').strip().upper()

    def clean(self):
        datos = super().clean()
        if datos.get('tipo') == Perfil.Tipo.MAYORISTA:
            if not datos.get('empresa'):
                self.add_error('empresa', 'Indica el nombre de tu empresa o negocio.')
            if not datos.get('telefono'):
                self.add_error('telefono', 'Necesitamos un teléfono para contactarte.')
        return datos

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.username = self.cleaned_data['email']
        usuario.email = self.cleaned_data['email']
        if commit:
            usuario.save()
            perfil, _ = Perfil.objects.get_or_create(usuario=usuario)
            perfil.tipo = self.cleaned_data['tipo']
            perfil.telefono = self.cleaned_data.get('telefono', '')
            perfil.empresa = self.cleaned_data.get('empresa', '')
            perfil.rfc = self.cleaned_data.get('rfc', '')
            perfil.save()
        return usuario


class EntrarForm(AuthenticationForm):
    username = forms.CharField(
        label='Correo electrónico',
        widget=forms.TextInput(attrs={'autofocus': True, 'autocomplete': 'email'})
    )

    def clean_username(self):
        return self.cleaned_data['username'].strip().lower()


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')
        labels = {'first_name': 'Nombre', 'last_name': 'Apellidos'}


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = (
            'telefono', 'empresa', 'rfc',
            'calle', 'colonia', 'ciudad', 'estado', 'codigo_postal',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.tipo != Perfil.Tipo.MAYORISTA:
            del self.fields['empresa']
            del self.fields['rfc']

    def clean_rfc(self):
        return self.cleaned_data.get('rfc', '').strip().upper()

    def clean_codigo_postal(self):
        cp = self.cleaned_data.get('codigo_postal', '').strip()
        if cp and (not cp.isdigit() or len(cp) != 5):
            raise forms.ValidationError('El código postal debe tener 5 dígitos.')
        return cp
