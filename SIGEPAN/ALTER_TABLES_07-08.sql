-- =====================================================================
-- ALTER TABLE consolidado — sesión 07-08-2026
-- Corre esto en tu MySQL real (SIGEPAN) antes de probar los cambios de
-- código de hoy. NINGUNO de estos requiere `python manage.py migrate`.
-- =====================================================================

-- RF-018: folio propio del ajuste (AJ000001, AJ000002, ...)
ALTER TABLE ajuste
    ADD COLUMN folio VARCHAR(20) NULL UNIQUE AFTER id_ajuste;

-- Corrección (07-08): apps.security era la única app del proyecto sin
-- managed=False, por lo que al mezclar el trabajo de César se generaron
-- dos migraciones nuevas (google_refresh_token, enum de log_acciones)
-- que iban a requerir correr `migrate` — algo que el equipo decidió
-- evitar. Se agregó managed=False a los 5 modelos de security y, en su
-- lugar, esta columna se agrega a mano igual que el resto del proyecto:
ALTER TABLE usuario
    ADD COLUMN google_refresh_token TEXT NULL AFTER google_token;

-- El cambio del ENUM de tipo_accion (CAMBIAR_USUARIO) y el fix de
-- fecha_creacion en rol_permiso ya estaban cubiertos por el
-- ALTER_TABLES_06-08.sql de la sesión anterior — no hace falta repetirlos
-- aquí si ya los corriste.
