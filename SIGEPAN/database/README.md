# SIGEPAN Database

## Versión

2.1 — actualizado 2026-08-04 (44 tablas, esquema real; se agregó `detalle_pago`)

## Motor

MySQL 8

## Scripts

01_create_database.sql

Crea la base de datos.

02_create_tables.sql

Crea las 43 tablas actuales (regenerado el 2026-08-04 con `mysqldump --no-data` /
Data Export "Dump Structure Only" desde la BD real de desarrollo — reemplaza la
versión anterior de 26 tablas, que estaba desactualizada frente al código).

## Backup

backup/02_create_tables_OBSOLETO_26tablas.sql, backup/03_alter_tables_OBSOLETO.sql,
backup/04_final_adjustments_OBSOLETO.sql

Versiones anteriores del esquema, ya incorporadas dentro del nuevo 02_create_tables.sql.
Se conservan solo como historial, no usar para provisionar una base nueva.

backup/sigepan_db_v1.sql

Respaldo oficial generado desde MySQL Workbench (versión anterior, ver 02_create_tables.sql
para el esquema vigente).

## Importante

Toda modificación de la base de datos deberá realizarse sobre los scripts del repositorio.

No modificar directamente la base de datos instalada.

`02_create_tables.sql` es ahora la fuente de verdad para levantar el esquema desde cero
(por ejemplo, en el contenedor MySQL de Docker). Si el esquema real cambia, regenerar este
archivo con `mysqldump --no-data --routines --triggers --add-drop-table sigepan_db` (o el
"Data Export → Dump Structure Only" de MySQL Workbench) y reemplazar este archivo.