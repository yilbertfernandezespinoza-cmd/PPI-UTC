#!/usr/bin/env python3
"""
==========================================================
SIGEPAN Developer Tools
create_module.py

Herramienta para generar automáticamente
la estructura estándar de un módulo SIGEPAN.
==========================================================
"""

from pathlib import Path
import sys


# ==========================================================
# Validar parámetros
# ==========================================================

if len(sys.argv) != 2:

    print("\nUso:")
    print("python scripts/create_module.py nombre_modulo\n")

    sys.exit(1)


# ==========================================================
# Nombre del módulo
# ==========================================================

module_name = sys.argv[1].lower()


# ==========================================================
# Ruta del proyecto
# ==========================================================

ROOT = Path(__file__).resolve().parent.parent

BACKEND = ROOT / "backend"

APPS = BACKEND / "apps"

MODULE = APPS / module_name


print("=" * 50)
print("SIGEPAN Developer Tools")
print("=" * 50)

print(f"Módulo : {module_name}")
print(f"Ruta   : {MODULE}")

print("=" * 50)

# ==========================================================
# Verificar si el módulo ya existe
# ==========================================================

if MODULE.exists():

    print("\n" + "=" * 50)
    print("SIGEPAN Developer Tools")
    print("=" * 50)

    print(f"\n⚠ El módulo '{module_name}' ya existe.")
    print("No se realizaron cambios.")

    print("\n" + "=" * 50)

    sys.exit(0)

# ==========================================================
# Crear estructura de carpetas
# ==========================================================

folders = [
    MODULE,
    MODULE / "migrations",
    MODULE / "templates",
    MODULE / "templates" / module_name,
    MODULE / "static",
    MODULE / "static" / module_name,
    MODULE / "static" / module_name / "css",
    MODULE / "static" / module_name / "js",
    MODULE / "static" / module_name / "img",
]

for folder in folders:
    folder.mkdir(parents=True, exist_ok=True)

print("\n✓ Estructura de carpetas creada correctamente.")

# ==========================================================
# Crear archivos base
# ==========================================================

files = [
    "__init__.py",
    "admin.py",
    "apps.py",
    "forms.py",
    "models.py",
    "repositories.py",
    "services.py",
    "tests.py",
    "urls.py",
    "validators.py",
    "filters.py",
    "views.py",
]

for file in files:

    file_path = MODULE / file

    if not file_path.exists():

        file_path.touch()


# __init__.py en migrations

migration_init = MODULE / "migrations" / "__init__.py"

if not migration_init.exists():

    migration_init.touch()


# Archivos .gitkeep

gitkeep_files = [

    MODULE / "templates" / module_name / ".gitkeep",

    MODULE / "static" / module_name / "css" / ".gitkeep",

    MODULE / "static" / module_name / "js" / ".gitkeep",

    MODULE / "static" / module_name / "img" / ".gitkeep",

]

for gitkeep in gitkeep_files:

    if not gitkeep.exists():

        gitkeep.touch()

print("✓ Archivos base creados correctamente.")

# ==========================================================
# Escribir contenido base
# ==========================================================

app_class = f"{module_name.capitalize()}Config"

# apps.py
apps_content = f'''from django.apps import AppConfig


class {app_class}(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.{module_name}"
    verbose_name = "{module_name.capitalize()}"
'''

(MODULE / "apps.py").write_text(apps_content, encoding="utf-8")


# urls.py
urls_content = '''from django.urls import path

urlpatterns = [

]
'''

(MODULE / "urls.py").write_text(urls_content, encoding="utf-8")


# Archivos con comentario inicial
base_files = {
    "forms.py": "# Formularios del módulo\n",
    "services.py": "# Servicios del módulo\n",
    "repositories.py": "# Repositorios del módulo\n",
    "validators.py": "# Validadores del módulo\n",
    "filters.py": "# Filtros del módulo\n",
}

for filename, content in base_files.items():
    (MODULE / filename).write_text(content, encoding="utf-8")

print("✓ Contenido base generado correctamente.")

# ==========================================================
# Resumen final
# ==========================================================

print("\n" + "=" * 60)
print("          SIGEPAN Developer Tools")
print("=" * 60)

print(f"✔ Módulo creado      : {module_name}")
print(f"✔ Ubicación          : {MODULE}")
print("✔ Carpetas           : OK")
print("✔ Archivos           : OK")
print("✔ Contenido base     : OK")

print("=" * 60)
print("Proceso finalizado correctamente.")
print("=" * 60)