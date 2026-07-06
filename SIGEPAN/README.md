Proceso que debe seguir César
1. Clonar el repositorio
git clone <url-del-repositorio>
cd SIGEPAN
2. Crear el entorno virtual
python -m venv venv

Activarlo:

Windows

venv\Scripts\activate
3. Instalar dependencias
pip install -r requirements.txt

Si todavía no existe el requirements.txt, lo generaremos una vez con:

pip freeze > requirements.txt

y lo subiremos al repositorio.

4. Crear el archivo .env

Debe tener la configuración de la base de datos.

Por ejemplo:

DB_ENGINE=django.db.backends.mysql
DB_NAME=sigepan_db
DB_USER=root
DB_PASSWORD=*******
DB_HOST=localhost
DB_PORT=3306

El .env no debe subirse a GitHub.

Lo ideal es subir un archivo .env.example con la estructura.

5. Importar la base de datos

Como nuestro proyecto es Database First, César debe importar el respaldo de la base de datos que ustedes definieron.

Por ejemplo:

sigepan_db.sql

Eso creará todas las tablas:

usuario
rol
permiso
producto
venta
etc.
6. Ejecutar únicamente las migraciones internas de Django (si son necesarias)

Como ya sincronizamos sessions, normalmente no debería tener que hacer nada si la base de datos ya incluye:

django_migrations
django_session
auth_*
django_content_type

Si por alguna razón recibe un aviso de migración pendiente para sessions y la tabla ya existe, ejecutará:

python manage.py migrate sessions --fake

No deberá ejecutar un python manage.py migrate completo, porque intentaría crear tablas de negocio que ya existen.

7. Ejecutar el servidor
python manage.py runserver

Y debería abrir correctamente:

http://127.0.0.1:8000