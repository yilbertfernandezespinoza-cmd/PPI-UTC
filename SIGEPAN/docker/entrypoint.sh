#!/bin/sh
set -e

echo "Esperando a que MySQL esté listo..."
python - <<'PYEOF'
import os
import socket
import sys
import time

host = os.environ.get("DB_HOST", "db")
port = int(os.environ.get("DB_PORT", "3306"))

for i in range(60):
    try:
        socket.create_connection((host, port), timeout=2).close()
        print("MySQL disponible.")
        sys.exit(0)
    except OSError:
        print(f"MySQL no responde todavía ({i + 1}/60)...")
        time.sleep(2)

print("No se pudo conectar a MySQL a tiempo.")
sys.exit(1)
PYEOF

# Corrección (08-08): NO correr "migrate" aquí. database/ddl/02_create_tables.sql
# ya incluye las tablas internas de Django (django_content_type,
# django_migrations, django_session, auth_user, etc.) porque es un volcado
# real de la base de datos del proyecto — son las mismas tablas que
# "migrate" intentaría crear, y como django_migrations queda vacía (se
# creó por SQL, no por migrate), Django no sabe que ya existen y falla con
# "Table ... already exists". El DDL ya es la única fuente de verdad del
# esquema (ver database/ddl/ y la regla del proyecto de no usar
# `manage.py migrate` — ver README.md).

echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando aplicación..."
exec "$@"
