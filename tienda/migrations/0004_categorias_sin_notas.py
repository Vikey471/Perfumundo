"""
Categorías principales en Marca (Árabes, Diseñador, Nicho) y se quitan
las notas olfativas: la información va en la descripción del perfume.
Las marcas existentes quedan como "Diseñador"; ajústalas en el admin.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tienda', '0003_catalogo_detallado'),
    ]

    operations = [
        migrations.AddField(
            model_name='marca',
            name='categoria',
            field=models.CharField(choices=[('arabe', 'Árabes'), ('disenador', 'Diseñador'), ('nicho', 'Nicho')], db_index=True, default='disenador', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name='marca',
            options={'ordering': ['categoria', 'nombre'], 'verbose_name': 'marca', 'verbose_name_plural': 'marcas'},
        ),
        migrations.RemoveField(model_name='producto', name='notas'),
        migrations.DeleteModel(name='ProductoNota'),
        migrations.DeleteModel(name='NotaOlfativa'),
        migrations.AlterField(
            model_name='producto',
            name='descripcion',
            field=models.TextField(help_text='Descripción breve del perfume (acordes, notas y estilo).'),
        ),
    ]
