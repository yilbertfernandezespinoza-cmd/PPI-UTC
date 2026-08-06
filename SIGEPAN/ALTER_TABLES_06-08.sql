-- =====================================================================
-- ALTER TABLE consolidado — sesión 06-08-2026
-- Corre esto en tu MySQL real (SIGEPAN) ANTES de probar los cambios de
-- código de hoy. Ninguno de estos ALTER rompe datos existentes: solo
-- agrega columnas nuevas o valores nuevos a un ENUM ya existente.
-- =====================================================================

-- RF-014/015: campo "turno" en apertura_caja (decisión: sí agregarlo)
ALTER TABLE apertura_caja
    ADD COLUMN turno VARCHAR(20) NULL DEFAULT NULL AFTER monto_inicial;

-- RF-034: nuevo valor CAMBIAR_USUARIO en el ENUM de log_acciones
-- (decisión: sí tocar el ENUM). Ajusta la lista de valores exactamente
-- a los que ya tenga tu tabla real antes de correr esto — usa
-- `SHOW COLUMNS FROM log_acciones LIKE 'tipo_accion';` para confirmarlos
-- primero si no estás seguro de que coincidan con esta lista.
ALTER TABLE log_acciones
    MODIFY tipo_accion ENUM(
        'LOGIN',
        'LOGOUT',
        'CREAR',
        'MODIFICAR',
        'ELIMINAR',
        'CONSULTAR',
        'EXPORTAR',
        'IMPORTAR',
        'ERROR',
        'ACCESO_DENEGADO',
        'RECUPERAR_PASSWORD',
        'CAMBIAR_PASSWORD',
        'CAMBIAR_USUARIO'
    ) NOT NULL;

-- RF-026: comprobante como archivo real en gasto_operativo (decisión:
-- sí, archivo adjunto real en vez de solo texto en observaciones)
ALTER TABLE gasto_operativo
    ADD COLUMN comprobante VARCHAR(255) NULL DEFAULT NULL AFTER observaciones;

-- RF-016: índice único (producto, sucursal) en inventario — evita que
-- se puedan crear dos filas de inventario para el mismo producto en la
-- misma sucursal (ya lo previene `obtener_o_crear()` en código, esto lo
-- refuerza también a nivel de base de datos).
ALTER TABLE inventario
    ADD CONSTRAINT uq_inventario_producto_sucursal
    UNIQUE (id_producto, id_sucursal);

-- =====================================================================
-- Ya existentes de sesiones anteriores (por si no los has corrido):
-- =====================================================================
-- ALTER TABLE ayuda ADD COLUMN imagen VARCHAR(255) DEFAULT NULL AFTER icono;

-- =====================================================================
-- NOTA (06-08): Productos y Categorías dejaron de ser excepción del
-- resto del proyecto. Antes eran las únicas dos apps sin managed=False
-- (usaban migraciones reales de Django). Se les agregó managed=False,
-- igual que el resto del sistema (Database First) — por eso YA NO hace
-- falta correr `python manage.py migrate productos` ni ningún otro
-- `migrate` para ellas. Sus carpetas migrations/ se dejan tal cual mas
-- quedan inertes, Django ya no las usa para nada.
-- =====================================================================

-- =====================================================================
-- Comandos de Django a correr en tu máquina después de los ALTER:
-- =====================================================================
-- python manage.py seed_metodos_pago
-- python manage.py seed_permisos_modulos
-- python manage.py seed_ayudas
-- python manage.py check
