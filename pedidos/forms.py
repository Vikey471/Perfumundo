from django import forms

from .models import Pedido


class DatosEnvioForm(forms.ModelForm):
    guardar_en_perfil = forms.BooleanField(
        label='Guardar esta dirección en mi cuenta',
        required=False,
        initial=True,
    )

    class Meta:
        model = Pedido
        fields = (
            'nombre', 'telefono', 'calle', 'colonia',
            'ciudad', 'estado_envio', 'codigo_postal', 'notas',
        )
        widgets = {'notas': forms.Textarea(attrs={'rows': 3})}

    def clean_codigo_postal(self):
        cp = self.cleaned_data['codigo_postal'].strip()
        if not cp.isdigit() or len(cp) != 5:
            raise forms.ValidationError('El código postal debe tener 5 dígitos.')
        return cp

    @classmethod
    def desde_perfil(cls, usuario):
        perfil = usuario.perfil
        return cls(initial={
            'nombre': usuario.get_full_name(),
            'telefono': perfil.telefono,
            'calle': perfil.calle,
            'colonia': perfil.colonia,
            'ciudad': perfil.ciudad,
            'estado_envio': perfil.estado,
            'codigo_postal': perfil.codigo_postal,
        })

    def datos_pedido(self):
        datos = dict(self.cleaned_data)
        datos.pop('guardar_en_perfil', None)
        return datos

    def guardar_en(self, perfil):
        d = self.cleaned_data
        perfil.telefono = d['telefono']
        perfil.calle = d['calle']
        perfil.colonia = d['colonia']
        perfil.ciudad = d['ciudad']
        perfil.estado = d['estado_envio']
        perfil.codigo_postal = d['codigo_postal']
        perfil.save()
