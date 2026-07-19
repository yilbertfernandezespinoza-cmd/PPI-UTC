from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("security", "0004_alter_logacciones_tipo_accion"),   # ← aquí luego revisamos si debe apuntar a otra
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
                    'ACCESO_DENEGADO',
                    'RECUPERAR_PASSWORD',
                    'CAMBIAR_PASSWORD'
                ) NOT NULL;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]