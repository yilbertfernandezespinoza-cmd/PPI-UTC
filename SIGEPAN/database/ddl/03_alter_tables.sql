-- ==========================================================
-- ALTER TABLE: venta
-- Agregar método de pago
-- ==========================================================

USE sigepan_db;

ALTER TABLE venta
ADD COLUMN id_metodo_pago INT UNSIGNED NOT NULL
AFTER id_caja;

ALTER TABLE venta
ADD CONSTRAINT fk_venta_metodo_pago
FOREIGN KEY (id_metodo_pago)
REFERENCES metodo_pago(id_metodo_pago);

-- ==========================================================
-- ALTER TABLE: producto
-- Agregar campos para RF-010 Gestión de Productos
-- ==========================================================

ALTER TABLE producto
ADD COLUMN porcentaje_utilidad DECIMAL(5,2) NOT NULL DEFAULT 30.00
AFTER precio_compra,

ADD COLUMN porcentaje_impuesto DECIMAL(5,2) NOT NULL DEFAULT 13.00
AFTER porcentaje_utilidad,

ADD COLUMN unidad_medida VARCHAR(30) NOT NULL DEFAULT 'Unidad'
AFTER porcentaje_impuesto;

-- ==========================================================
-- ALTER TABLE: usuario
-- Agregar sucursal e integración con Google
-- ==========================================================

ALTER TABLE usuario

ADD COLUMN id_sucursal INT UNSIGNED NULL
AFTER id_rol,

ADD COLUMN google_email VARCHAR(150) NULL
AFTER email,

ADD COLUMN google_id VARCHAR(150) NULL
AFTER google_email,

ADD COLUMN google_token TEXT NULL
AFTER google_id;

ALTER TABLE usuario

ADD CONSTRAINT fk_usuario_sucursal
FOREIGN KEY (id_sucursal)
REFERENCES sucursal(id_sucursal);

-- ==========================================================
-- ALTER TABLE: venta
-- Agregar consecutivo y tipo de comprobante
-- ==========================================================

ALTER TABLE venta

ADD COLUMN numero_venta VARCHAR(30) NOT NULL
AFTER id_venta,

ADD COLUMN tipo_comprobante ENUM(
    'TICKET',
    'FACTURA'
) NOT NULL DEFAULT 'TICKET'
AFTER numero_venta;

-- ==========================================================
-- ALTER TABLE: producto
-- Eliminar stock_minimo
-- ==========================================================

ALTER TABLE producto
DROP COLUMN stock_minimo;

-- ==========================================================
-- ALTER TABLE: producto
-- Eliminar relación directa con proveedor
-- ==========================================================

ALTER TABLE producto
DROP FOREIGN KEY fk_producto_proveedor;

ALTER TABLE producto
DROP COLUMN id_proveedor;