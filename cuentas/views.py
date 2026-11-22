from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import EntrarForm, PerfilForm, RegistroForm, UsuarioForm
from .models import Perfil


def registro(request):
    if request.user.is_authenticated:
        return redirect('mi_cuenta')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario, backend='django.contrib.auth.backends.ModelBackend')
            if usuario.perfil.mayorista_pendiente:
                messages.info(
                    request,
                    'Tu cuenta está lista. Revisaremos tu solicitud de mayorista '
                    'y te avisaremos cuando quede aprobada.'
                )
            else:
                messages.success(request, '¡Bienvenido a Perfumundo!')
            return redirect('mi_cuenta')
    else:
        form = RegistroForm()

    return render(request, 'cuentas/registro.html', {'form': form})


class EntrarView(auth_views.LoginView):
    template_name = 'cuentas/entrar.html'
    authentication_form = EntrarForm
    redirect_authenticated_user = True


@login_required
def mi_cuenta(request):
    perfil, _ = Perfil.objects.get_or_create(usuario=request.user)

    if request.method == 'POST':
        usuario_form = UsuarioForm(request.POST, instance=request.user)
        perfil_form = PerfilForm(request.POST, instance=perfil)
        if usuario_form.is_valid() and perfil_form.is_valid():
            usuario_form.save()
            perfil_form.save()
            messages.success(request, 'Tus datos se guardaron.')
            return redirect('mi_cuenta')
    else:
        usuario_form = UsuarioForm(instance=request.user)
        perfil_form = PerfilForm(instance=perfil)

    return render(request, 'cuentas/mi_cuenta.html', {
        'perfil': perfil,
        'usuario_form': usuario_form,
        'perfil_form': perfil_form,
    })
