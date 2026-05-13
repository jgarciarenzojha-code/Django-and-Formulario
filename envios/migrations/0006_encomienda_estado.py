# Generated for DRF final deliverable

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('envios', '0005_historialestado'),
    ]

    operations = [
        migrations.AddField(
            model_name='encomienda',
            name='estado',
            field=models.CharField(
                choices=[
                    ('pendiente', 'Pendiente'),
                    ('en_transito', 'En transito'),
                    ('entregada', 'Entregada'),
                    ('cancelada', 'Cancelada'),
                ],
                default='pendiente',
                max_length=20,
            ),
        ),
    ]
