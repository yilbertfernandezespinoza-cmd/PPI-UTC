# SIGEPAN

Sistema de información para la gestión operativa y administrativa de una
panadería ("La Pana"): ventas, inventario, compras, clientes, proveedores,
mermas, gastos operativos, caja y seguridad de acceso por roles.

Proyecto desarrollado para el curso Proyecto Profesional Informático,
Universidad Tecnológica Costarricense.

## Tecnologías principales

- **Backend:** Python 3.12+, Django 6.0.6 (patrón MVT)
- **Base de datos:** MySQL 8.0 — enfoque **Database First**: el esquema se
  define en `database/ddl/`, Django se conecta a las tablas ya existentes
  y **no gestiona migraciones de esquema** para los modelos de negocio
  (todos los modelos tienen `managed = False`).
- **Frontend:** Bootstrap 5, AdminLTE, DataTables/Tabulator
- **Reportes:** ReportLab (PDF), OpenPyXL (Excel), Google Sheets API
- **Autenticación:** login propio + Google OAuth 2.0 (opcional)
- **Infraestructura:** Docker, Docker Compose, Cloudflare Tunnel

## Requisitos previos

- Python 3.12 o superior — **instalado desde
  [python.org/downloads](https://www.python.org/downloads/)**, marcando
  la opción "Add python.exe to PATH" durante la instalación. **No usar
  la versión de Python de Microsoft Store**: corre en una sandbox con
  permisos restringidos que hace fallar la creación del entorno virtual
  (falla silenciosamente al instalar pip adentro del `venv`). Para
  revisar cuál tienes activo: `Get-Command python` en PowerShell — si la
  ruta contiene `WindowsApps`, es la de Store y hay que reinstalar.
- MySQL 8.0
- Git

## ⚠ Antes de compartir el proyecto por carpeta (sin Git)

Si van a entregar el proyecto comprimiendo la carpeta a mano (no
mediante `git clone`), revisen que **no** venga incluida ninguna de
estas carpetas — son específicas de cada máquina y su sola presencia
rompe la instalación en la máquina de quien lo reciba (el `venv` no es
portable: los `.exe` dentro de `venv\Scripts\` traen grabada la ruta
absoluta de la PC donde se creó):

- `venv/` o `.venv/`
- `__pycache__/` (en cualquier subcarpeta)
- `.git/` (si existe, no hace falta para instalar y pesa mucho)
- `backend/.env` (tiene credenciales propias — se comparte solo
  `.env.example`)

## Instalación local (sin Docker)

> **Nota sobre la terminal:** los comandos de esta sección están en dos
> columnas porque **PowerShell (la terminal que abre VS Code por
> defecto en Windows) no es bash**: no soporta `source` para activar el
> entorno virtual ni `<` para redirigir un archivo hacia otro programa.
> Si tu terminal muestra un prompt como `PS C:\...>`, estás en
> PowerShell — usa la columna de Windows. Si usas Git Bash, WSL,
> Linux o macOS, usa la columna de bash.

### 1. Obtener el proyecto

Si lo recibiste como carpeta comprimida (no por Git), descomprímela y
ubica **la carpeta que tiene `backend/`, `database/` y
`requirements.txt` directamente adentro** (todavía NO entres a
`backend/` — eso es hasta el paso 6). Ojo: al descomprimir es muy común
que quede una carpeta duplicada (`SIGEPAN\SIGEPAN`, una dentro de otra
con el mismo nombre) — si pasa eso, la carpeta correcta es la de
adentro, no la de afuera.

Para que la terminal quede parada exactamente ahí: en el Explorador de
Windows, entra a esa carpeta, haz clic derecho en un espacio vacío y
elige **"Abrir en Terminal"** (o "Open PowerShell window here"). Se abre
una PowerShell ya ubicada ahí — confírmalo con `dir` y revisa que
aparezcan `backend`, `database` y `requirements.txt` en la lista. Todos
los comandos de los pasos 2 a 5 se ejecutan parado ahí, sin volver a
moverte de carpeta.

Si lo vas a clonar con Git:

PowerShell / cmd (Windows):
```powershell
git clone <url-del-repositorio>
cd PPI\SIGEPAN
```

bash (Git Bash / Linux / macOS):
```bash
git clone <url-del-repositorio>
cd PPI/SIGEPAN
```

### 2. Crear y activar el entorno virtual

**Importante:** los dos comandos siguientes se ejecutan uno después del
otro, sin cambiar de carpeta entre ellos — `venv` se crea dentro de la
carpeta donde estés parado en ese momento (la misma del paso 1), y hay
que activarlo desde esa misma carpeta. Si te da "no se reconoce" al
activar, seguramente cambiaste de carpeta o estás usando una ruta que no
coincide (revisa que no te hayas quedado un nivel arriba o abajo de una
carpeta `SIGEPAN` duplicada).

PowerShell (Windows):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
Si `python` no se reconoce, prueba con `py -3 -m venv venv`. Si al
activar sale un error de "la ejecución de scripts está deshabilitada en
este sistema", ejecuta esto una sola vez y vuelve a intentar:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

bash (Git Bash / Linux / macOS):
```bash
python -m venv venv
source venv/bin/activate
```

En ambos casos, si funcionó vas a ver `(venv)` al inicio de la línea de
comandos.

### 3. Instalar dependencias

```
pip install -r requirements.txt
```
(igual en PowerShell y en bash, siempre con el entorno virtual activado)

### 4. Configurar variables de entorno

Copia `backend/.env.example` como `backend/.env` y completa los valores
reales (credenciales de base de datos, correo, y opcionalmente Google
OAuth). El archivo `.env` nunca debe subirse a Git.

PowerShell:
```powershell
Copy-Item backend\.env.example backend\.env
```
bash:
```bash
cp backend/.env.example backend/.env
```

### 5. Crear la base de datos (Database First)

Como el proyecto no usa migraciones de Django para las tablas de negocio,
la base de datos se crea ejecutando los scripts DDL en orden. **Esta es
la parte que falla si la corres tal cual en PowerShell** — el operador
`<` no funciona ahí, hay que pasarlo por `cmd /c`:

PowerShell (Windows):
```powershell
cmd /c "mysql -u root -p < database\ddl\01_create_database.sql"
cmd /c "mysql -u root -p sigepan_db < database\ddl\02_create_tables.sql"
```

bash (Git Bash / Linux / macOS):
```bash
mysql -u root -p < database/ddl/01_create_database.sql
mysql -u root -p sigepan_db < database/ddl/02_create_tables.sql
```

Si `mysql` no se reconoce como comando, es que la carpeta `bin` de tu
instalación de MySQL no está en el PATH — busca `mysql.exe` dentro de
`C:\Program Files\MySQL\MySQL Server 8.0\bin` (o donde lo hayas
instalado) y usa la ruta completa en vez de solo `mysql`.

**Alternativa sin terminal (MySQL Workbench):** si prefieres evitar la
línea de comandos, abre MySQL Workbench, conéctate a tu servidor local,
y en el menú `File → Open SQL Script` abre primero
`database/ddl/01_create_database.sql` y ejecútalo (ícono de rayo o
Ctrl+Shift+Enter). Repite lo mismo con `02_create_tables.sql`, pero
antes selecciona `sigepan_db` como base activa (doble clic sobre el
esquema en el panel izquierdo) para que las tablas se creen ahí y no en
otra base.

Esto crea todas las tablas del sistema con su estructura actual y
actualizada (incluye todos los cambios de esquema aplicados durante el
desarrollo — no hace falta ejecutar ningún script adicional).

**No ejecutar `python manage.py migrate`** para las apps de negocio: todas
tienen `managed = False` porque las tablas ya existen en la base de datos
importada arriba. La única excepción son las tablas internas propias de
Django (sesiones, etc.), que si llegan a hacer falta se resuelven con
`python manage.py migrate sessions` — no debería ser necesario en una
instalación nueva.

### 6. Cargar datos iniciales (catálogos)

```bash
cd backend
python manage.py seed_admin
python manage.py seed_permisos_modulos
python manage.py seed_metodos_pago
python manage.py seed_tipos_movimiento
python manage.py seed_ayudas
```

> **Nota:** el script DDL crea las tablas vacías, sin ningún usuario. Como
> SIGEPAN usa un modelo de `Usuario` propio (no el sistema de auth de
> Django), `seed_admin` es el que resuelve esto: crea una sucursal, un
> rol "Administrador" con el catálogo completo de permisos, y un usuario
> con el que ya se puede iniciar sesión:
>
> - **Usuario:** `admin`
> - **Contraseña:** `Admin123*`
>
> Cambia la contraseña desde "Mi perfil" apenas inicies sesión. El
> comando es idempotente: correrlo de nuevo no duplica ni pisa datos ya
> existentes.

**Opcional — datos de ejemplo:** si quieres ver el sistema funcionando
con contenido real (POS, reportes, dashboard con alertas de stock bajo)
en vez de completamente vacío, corre además:
```
python manage.py seed_productos_demo
```
Crea 20 productos de panadería de ejemplo, sus categorías, y su
inventario inicial en "Sucursal Principal" (4 de ellos a propósito con
stock bajo, para ver la alerta del dashboard funcionando). No es
necesario para que el sistema funcione — solo para tener datos con qué
probarlo.

### 7. Ejecutar el servidor

```bash
python manage.py runserver
```

El sistema queda disponible en `http://127.0.0.1:8000`.

## Instalación con Docker (servidor propio + Cloudflare Tunnel)

El proyecto incluye `docker-compose.yml` con tres servicios: base de
datos MySQL (se inicializa sola con los scripts de `database/ddl/`), la
aplicación Django (Gunicorn) y Cloudflare Tunnel, que expone el sistema
a internet con un dominio propio y HTTPS **sin abrir puertos del
router**. Esta es la vía pensada para levantar SIGEPAN en un servidor
propio (una PC o mini-servidor en casa/local), no solo para desarrollo.

### 1. Requisitos en el servidor

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
  (Windows/macOS) o Docker Engine + el plugin `docker compose`
  (Linux), instalado y corriendo.
- Una cuenta de [Cloudflare](https://dash.cloudflare.com/) (gratis) con
  un dominio agregado (puede ser uno comprado barato solo para esto —
  Cloudflare Tunnel necesita un dominio propio en su DNS, no funciona
  con cualquier dominio).

### 2. Crear el túnel de Cloudflare

1. Entra a [Cloudflare Zero Trust](https://one.dash.cloudflare.com/) →
   **Networks → Tunnels → Create a tunnel**.
2. Elige **Cloudflared**, ponle un nombre (ej. `sigepan`) y créalo.
3. En el paso "Install and run a connector", **no instales nada ahí** —
   solo copia el token largo que aparece después de `--token` en el
   comando de ejemplo. Ese token va en `CLOUDFLARE_TUNNEL_TOKEN` del
   `.env.production` (paso 3). El contenedor `cloudflared` del
   `docker-compose.yml` hace ese trabajo por ti, no hace falta instalar
   `cloudflared` a mano en el servidor.
4. En **Public Hostname**, agrega uno nuevo:
   - **Subdomain:** lo que quieras (ej. `sigepan`)
   - **Domain:** el dominio que tengas en Cloudflare
   - **Type:** `HTTP`
   - **URL:** `web:8000` (el nombre del servicio `web` de
     `docker-compose.yml`, tal cual, no una IP ni `localhost`)
5. Guarda. Ese subdominio completo (ej. `sigepan.tudominio.com`) es la
   URL pública del sistema — la vas a necesitar en el siguiente paso.

### 3. Configurar `.env.production`

Copia la plantilla y complétala con los valores reales:

PowerShell:
```powershell
Copy-Item .env.production.example .env.production
notepad .env.production
```
bash:
```bash
cp .env.production.example .env.production
nano .env.production
```

Revisa especialmente:
- `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` con el subdominio real del
  paso 2 (ej. `sigepan.tudominio.com` y
  `https://sigepan.tudominio.com`).
- `DB_HOST=db` (no `127.0.0.1` — es el nombre del contenedor de MySQL,
  no aplica el mismo valor que en instalación local).
- `DB_ROOT_PASSWORD` y `DB_PASSWORD`: contraseñas nuevas que tú
  eliges, no las de ninguna instalación anterior.
- `CLOUDFLARE_TUNNEL_TOKEN`: el token del paso 2.
- Si usan Google OAuth: `GOOGLE_REDIRECT_URI` con el dominio público
  real (https, sin puerto), y agregar esa misma URL exacta en Google
  Cloud Console → Credenciales → tu Client ID → "URI de
  redireccionamiento autorizados" — si no coincide letra por letra
  (incluida la barra final), Google rechaza el login.

### 4. Levantar el stack

```
docker compose up -d --build
```

La primera vez tarda varios minutos (construye la imagen, MySQL se
inicializa con el DDL, corren las migraciones internas de Django). Para
ver el progreso o diagnosticar errores:
```
docker compose logs -f web
```

### 5. Cargar los datos iniciales

El DDL crea las tablas vacías igual que en la instalación local — hay
que sembrar los catálogos y el usuario admin dentro del contenedor:

```
docker compose exec web python manage.py seed_admin
docker compose exec web python manage.py seed_permisos_modulos
docker compose exec web python manage.py seed_metodos_pago
docker compose exec web python manage.py seed_tipos_movimiento
docker compose exec web python manage.py seed_ayudas
```
(y opcionalmente `docker compose exec web python manage.py seed_productos_demo`
para tener datos de ejemplo — ver la nota en el paso 6 de la instalación
local).

### 6. Verificar

Entra a `https://tu-subdominio.tudominio.com` desde cualquier
dispositivo con internet — no hace falta estar en la misma red del
servidor. Inicia sesión con `admin` / `Admin123*` (paso 5) y cambia la
contraseña desde "Mi perfil".

### Comandos útiles

```
docker compose ps                    # estado de los 3 contenedores
docker compose logs -f web           # logs de Django en vivo
docker compose logs -f cloudflared   # logs del túnel (si no conecta)
docker compose down                  # apagar todo (sin borrar datos)
docker compose down -v               # apagar y borrar también los volúmenes (¡borra la BD!)
```

## Estructura del proyecto

```
SIGEPAN/
├── backend/            Proyecto Django (apps, templates, estáticos)
├── database/ddl/       Esquema de base de datos (Database First)
├── docker/             Configuración de contenedores
├── scripts/            Utilidades de desarrollo
└── Entregable5/        Documentación de entrega del curso
```

## Convenciones del proyecto

- **Arquitectura por app:** `models.py` → `repositories.py` (acceso a
  datos) → `services.py` (lógica de negocio) → `views.py` (delgadas).
- **Base de datos:** cualquier cambio de esquema se aplica con SQL manual
  contra la base real y se refleja después en `database/ddl/`, nunca con
  `migrate`.
- **Auditoría:** las acciones relevantes quedan registradas en la
  bitácora del sistema (módulo Seguridad).
