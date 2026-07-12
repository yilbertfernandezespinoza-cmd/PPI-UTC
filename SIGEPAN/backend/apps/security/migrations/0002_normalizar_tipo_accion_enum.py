from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("security", "0001_initial"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE log_acciones
                MODIFY COLUMN tipo_accion ENUM(
                    'LOGIN',
                    'LOGOUT',
                    'CONSULTAR',
                    'CREAR',
                    'MODIFICAR',
                    'ELIMINAR',
                    'EXPORTAR',
                    'IMPORTAR',
                    'ERROR',
                    'ACCESO_DENEGADO'
                ) NOT NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]