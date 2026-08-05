# Generado a mano el 2026-08-04 (RF-011): agrega `choices` a unidad_medida.
# No cambia el tipo ni el tamaño de la columna (sigue siendo varchar(30)),
# así que no hay riesgo para los productos ya guardados en la base de datos.
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='unidad_medida',
            field=models.CharField(
                choices=[
                    ('Unidad', 'Unidad'),
                    ('Docena', 'Docena'),
                    ('Kilogramo', 'Kilogramo (kg)'),
                    ('Gramo', 'Gramo (g)'),
                    ('Libra', 'Libra (lb)'),
                    ('Litro', 'Litro (l)'),
                    ('Mililitro', 'Mililitro (ml)'),
                    ('Paquete', 'Paquete'),
                    ('Caja', 'Caja'),
                    ('Bolsa', 'Bolsa'),
                ],
                default='Unidad',
                max_length=30,
            ),
        ),
    ]
