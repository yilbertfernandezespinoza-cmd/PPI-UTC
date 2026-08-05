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

echo "Aplicando migraciones internas de Django (sessions/admin/contenttypes/auth)..."
python manage.py migrate --noinput

echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "Iniciando aplicación..."
exec "$@"
