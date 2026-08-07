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

- Python 3.12 o superior
- MySQL 8.0
- Git

## Instalación local (sin Docker)

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd PPI/SIGEPAN
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv venv
```

Windows:
```bash
venv\Scripts\activate
```

Linux/macOS:
```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copia `backend/.env.example` como `backend/.env` y completa los valores
reales (credenciales de base de datos, correo, y opcionalmente Google
OAuth). El archivo `.env` nunca debe subirse a Git.

### 5. Crear la base de datos (Database First)

Como el proyecto no usa migraciones de Django para las tablas de negocio,
la base de datos se crea ejecutando los scripts DDL en orden:

```bash
mysql -u root -p < database/ddl/01_create_database.sql
mysql -u root -p sigepan_db < database/ddl/02_create_tables.sql
```

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

### 7. Ejecutar el servidor

```bash
python manage.py runserver
```

El sistema queda disponible en `http://127.0.0.1:8000`.

## Instalación con Docker

El proyecto incluye `docker-compose.yml` con tres servicios: base de
datos MySQL (que se inicializa automáticamente con los scripts de
`database/ddl/`), la aplicación Django, y Cloudflare Tunnel (opcional,
para exponer el sistema a internet sin abrir puertos).

```bash
cp backend/.env.example .env.production
# completar .env.production con los valores reales
docker compose up -d --build
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
