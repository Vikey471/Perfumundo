from django.conf import settings
from django.db import migrations


def crear_perfiles(apps, schema_editor):
    """Crea un perfil para los usuarios que ya existían antes de esta app."""
    app_label, model_name = settings.AUTH_USER_MODEL.split('.')
    User = apps.get_model(app_label, model_name)
    Perfil = apps.get_model('cuentas', 'Perfil')
    for usuario in User.objects.filter(perfil__isnull=True):
        Perfil.objects.create(usuario=usuario)


class Migration(migrations.Migration):

    dependencies = [
        ('cuentas', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(crear_perfiles, migrations.RunPython.noop),
    ]
