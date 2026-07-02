-- ==========================================================
-- PROYECTO : SIGEPAN
-- ARCHIVO  : 02_create_tables.sql
-- DESCRIPCIÓN:
-- Creación de tablas principales del sistema
-- ==========================================================

USE sigepan_db;

-- ==========================================================
-- TABLA: cargo
-- ==========================================================

CREATE TABLE cargo (

    id_cargo INT UNSIGNED AUTO_INCREMENT,

    nombre VARCHAR(100) NOT NULL,

    descripcion VARCHAR(255),

    estado BOOLEAN NOT NULL DEFAULT TRUE,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_cargo PRIMARY KEY (id_cargo),

    CONSTRAINT uk_cargo_nombre UNIQUE (nombre)

) ENGINE=InnoDB;

-- ==========================================================
-- TABLA: modulo
-- ==========================================================

CREATE TABLE modulo (

    id_modulo INT UNSIGNED AUTO_INCREMENT,

    nombre VARCHAR(100) NOT NULL,

    descripcion VARCHAR(255),

    icono VARCHAR(100),

    ruta VARCHAR(150),

    orden_menu INT NOT NULL DEFAULT 0,

    estado BOOLEAN NOT NULL DEFAULT TRUE,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_modulo PRIMARY KEY (id_modulo),

    CONSTRAINT uk_modulo_nombre UNIQUE (nombre)

) ENGINE=InnoDB;

-- ==========================================================
-- TABLA: rol
-- ==========================================================

CREATE TABLE rol (

    id_rol INT UNSIGNED AUTO_INCREMENT,

    nombre VARCHAR(100) NOT NULL,

    descripcion VARCHAR(255),

    estado BOOLEAN NOT NULL DEFAULT TRUE,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_rol PRIMARY KEY (id_rol),

    CONSTRAINT uk_rol_nombre UNIQUE (nombre)

) ENGINE=InnoDB;

-- ==========================================================
-- TABLA: permiso
-- ==========================================================

CREATE TABLE permiso (

    id_permiso INT UNSIGNED AUTO_INCREMENT,

    id_modulo INT UNSIGNED NOT NULL,

    accion VARCHAR(50) NOT NULL,

    descripcion VARCHAR(255),

    estado BOOLEAN NOT NULL DEFAULT TRUE,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_permiso PRIMARY KEY (id_permiso),

    CONSTRAINT fk_permiso_modulo
        FOREIGN KEY (id_modulo)
        REFERENCES modulo(id_modulo),

    CONSTRAINT uk_permiso UNIQUE (id_modulo, accion)

) ENGINE=InnoDB;

-- ==========================================================
-- TABLA: rol_permiso
-- ==========================================================

CREATE TABLE rol_permiso (

    id_rol_permiso INT UNSIGNED AUTO_INCREMENT,

    id_rol INT UNSIGNED NOT NULL,

    id_permiso INT UNSIGNED NOT NULL,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_rol_permiso PRIMARY KEY (id_rol_permiso),

    CONSTRAINT fk_rol_permiso_rol
        FOREIGN KEY (id_rol)
        REFERENCES rol(id_rol),

    CONSTRAINT fk_rol_permiso_permiso
        FOREIGN KEY (id_permiso)
        REFERENCES permiso(id_permiso),

    CONSTRAINT uk_rol_permiso UNIQUE (id_rol, id_permiso)

) ENGINE=InnoDB;


-- ==========================================================
-- TABLA: empleado
-- ==========================================================

CREATE TABLE empleado (

    id_empleado INT UNSIGNED AUTO_INCREMENT,

    id_cargo INT UNSIGNED NOT NULL,

    identificacion VARCHAR(20) NOT NULL,

    nombre VARCHAR(100) NOT NULL,

    apellido1 VARCHAR(100) NOT NULL,

    apellido2 VARCHAR(100),

    telefono VARCHAR(20),

    correo VARCHAR(150),

    direccion VARCHAR(255),

    fecha_ingreso DATE,

    estado BOOLEAN NOT NULL DEFAULT TRUE,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_empleado PRIMARY KEY (id_empleado),

    CONSTRAINT uk_empleado_identificacion UNIQUE (identificacion),

    CONSTRAINT fk_empleado_cargo
        FOREIGN KEY (id_cargo)
        REFERENCES cargo(id_cargo)

) ENGINE=InnoDB;

-- ==========================================================
-- TABLA: usuario
-- ==========================================================

CREATE TABLE usuario (

    id_usuario INT UNSIGNED AUTO_INCREMENT,

    id_empleado INT UNSIGNED NOT NULL,

    id_rol INT UNSIGNED NOT NULL,

    username VARCHAR(150) NOT NULL,

    password VARCHAR(255) NOT NULL,

    email VARCHAR(150),

    ultimo_acceso DATETIME,

    estado BOOLEAN NOT NULL DEFAULT TRUE,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_usuario PRIMARY KEY (id_usuario),

    CONSTRAINT uk_usuario_username UNIQUE (username),

    CONSTRAINT uk_usuario_empleado UNIQUE (id_empleado),

    CONSTRAINT fk_usuario_empleado
        FOREIGN KEY (id_empleado)
        REFERENCES empleado(id_empleado),

    CONSTRAINT fk_usuario_rol
        FOREIGN KEY (id_rol)
        REFERENCES rol(id_rol)

) ENGINE=InnoDB;

-- ==========================================================
-- TABLA: categoria
-- ==========================================================

CREATE TABLE categoria (

    id_categoria INT UNSIGNED AUTO_INCREMENT,

    nombre VARCHAR(100) NOT NULL,

    descripcion VARCHAR(255),

    estado BOOLEAN NOT NULL DEFAULT TRUE,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_categoria PRIMARY KEY (id_categoria),

    CONSTRAINT uk_categoria_nombre UNIQUE (nombre)

) ENGINE=InnoDB;

-- ==========================================================
-- TABLA: cliente
-- ==========================================================

CREATE TABLE cliente (

    id_cliente INT UNSIGNED AUTO_INCREMENT,

    identificacion VARCHAR(20),

    nombre VARCHAR(100) NOT NULL,

    apellido1 VARCHAR(100),

    apellido2 VARCHAR(100),

    telefono VARCHAR(20),

    correo VARCHAR(150),

    direccion VARCHAR(255),

    estado BOOLEAN NOT NULL DEFAULT TRUE,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_cliente PRIMARY KEY (id_cliente),

    CONSTRAINT uk_cliente_identificacion UNIQUE (identificacion)

) ENGINE=InnoDB;

-- ==========================================================
-- TABLA: proveedor
-- ==========================================================

CREATE TABLE proveedor (

    id_proveedor INT UNSIGNED AUTO_INCREMENT,

    identificacion VARCHAR(20),

    nombre VARCHAR(150) NOT NULL,

    contacto VARCHAR(100),

    telefono VARCHAR(20),

    correo VARCHAR(150),

    direccion VARCHAR(255),

    estado BOOLEAN NOT NULL DEFAULT TRUE,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_proveedor PRIMARY KEY (id_proveedor),

    CONSTRAINT uk_proveedor_identificacion UNIQUE (identificacion)

) ENGINE=InnoDB;

-- ==========================================================
-- TABLA: producto
-- ==========================================================

CREATE TABLE producto (

    id_producto INT UNSIGNED AUTO_INCREMENT,

    id_categoria INT UNSIGNED NOT NULL,

    id_proveedor INT UNSIGNED,

    codigo VARCHAR(50) NOT NULL,

    nombre VARCHAR(150) NOT NULL,

    descripcion VARCHAR(255),

    precio_compra DECIMAL(10,2) NOT NULL,

    precio_venta DECIMAL(10,2) NOT NULL,

    stock_minimo INT NOT NULL DEFAULT 0,

    imagen VARCHAR(255),

    estado BOOLEAN NOT NULL DEFAULT TRUE,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_producto PRIMARY KEY (id_producto),

    CONSTRAINT uk_producto_codigo UNIQUE (codigo),

    CONSTRAINT fk_producto_categoria
        FOREIGN KEY (id_categoria)
        REFERENCES categoria(id_categoria),

    CONSTRAINT fk_producto_proveedor
        FOREIGN KEY (id_proveedor)
        REFERENCES proveedor(id_proveedor)

) ENGINE=InnoDB;

-- ==========================================================
-- TABLA: inventario
-- ==========================================================

CREATE TABLE inventario (

    id_inventario INT UNSIGNED AUTO_INCREMENT,

    id_producto INT UNSIGNED NOT NULL,

    existencia INT NOT NULL DEFAULT 0,

    stock_minimo INT NOT NULL DEFAULT 0,

    stock_maximo INT DEFAULT 0,

    ubicacion VARCHAR(100),

    estado BOOLEAN NOT NULL DEFAULT TRUE,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_inventario PRIMARY KEY (id_inventario),

    CONSTRAINT uk_inventario_producto UNIQUE (id_producto),

    CONSTRAINT fk_inventario_producto
        FOREIGN KEY (id_producto)
        REFERENCES producto(id_producto)

) ENGINE=InnoDB;

-- ==========================================================
-- TABLA: compra
-- ==========================================================

CREATE TABLE compra (

    id_compra INT UNSIGNED AUTO_INCREMENT,

    id_proveedor INT UNSIGNED NOT NULL,

    id_usuario INT UNSIGNED NOT NULL,

    fecha DATE NOT NULL,

    total DECIMAL(12,2) NOT NULL,

    observaciones VARCHAR(255),

    estado BOOLEAN NOT NULL DEFAULT TRUE,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_compra PRIMARY KEY (id_compra),

    CONSTRAINT fk_compra_proveedor
        FOREIGN KEY (id_proveedor)
        REFERENCES proveedor(id_proveedor),

    CONSTRAINT fk_compra_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)

) ENGINE=InnoDB;

-- ==========================================================
-- TABLA: detalle_compra
-- ==========================================================

CREATE TABLE detalle_compra (

    id_detalle_compra INT UNSIGNED AUTO_INCREMENT,

    id_compra INT UNSIGNED NOT NULL,

    id_producto INT UNSIGNED NOT NULL,

    cantidad INT NOT NULL,

    precio_unitario DECIMAL(10,2) NOT NULL,

    subtotal DECIMAL(12,2) NOT NULL,

    CONSTRAINT pk_detalle_compra PRIMARY KEY (id_detalle_compra),

    CONSTRAINT fk_detalle_compra_compra
        FOREIGN KEY (id_compra)
        REFERENCES compra(id_compra),

    CONSTRAINT fk_detalle_compra_producto
        FOREIGN KEY (id_producto)
        REFERENCES producto(id_producto)

) ENGINE=InnoDB;

-- ==========================================================
-- TABLA: caja
-- ==========================================================

CREATE TABLE caja (

    id_caja INT UNSIGNED AUTO_INCREMENT,

    nombre VARCHAR(100) NOT NULL,

    descripcion VARCHAR(255),

    saldo_inicial DECIMAL(12,2) NOT NULL DEFAULT 0,

    saldo_actual DECIMAL(12,2) NOT NULL DEFAULT 0,

    estado BOOLEAN NOT NULL DEFAULT TRUE,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_caja PRIMARY KEY (id_caja),

    CONSTRAINT uk_caja_nombre UNIQUE (nombre)

) ENGINE=InnoDB;

-- ==========================================================
-- TABLA: venta
-- ==========================================================

CREATE TABLE venta (

    id_venta INT UNSIGNED AUTO_INCREMENT,

    id_cliente INT UNSIGNED,

    id_usuario INT UNSIGNED NOT NULL,

    id_caja INT UNSIGNED NOT NULL,

    fecha DATE NOT NULL,

    subtotal DECIMAL(12,2) NOT NULL,

    impuesto DECIMAL(12,2) NOT NULL DEFAULT 0,

    descuento DECIMAL(12,2) NOT NULL DEFAULT 0,

    total DECIMAL(12,2) NOT NULL,

    estado BOOLEAN NOT NULL DEFAULT TRUE,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_venta PRIMARY KEY (id_venta),

    CONSTRAINT fk_venta_cliente
        FOREIGN KEY (id_cliente)
        REFERENCES cliente(id_cliente),

    CONSTRAINT fk_venta_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario),

    CONSTRAINT fk_venta_caja
        FOREIGN KEY (id_caja)
        REFERENCES caja(id_caja)

) ENGINE=InnoDB;

-- ==========================================================
-- TABLA: detalle_venta
-- ==========================================================

CREATE TABLE detalle_venta (

    id_detalle_venta INT UNSIGNED AUTO_INCREMENT,

    id_venta INT UNSIGNED NOT NULL,

    id_producto INT UNSIGNED NOT NULL,

    cantidad INT NOT NULL,

    precio_unitario DECIMAL(10,2) NOT NULL,

    subtotal DECIMAL(12,2) NOT NULL,

    CONSTRAINT pk_detalle_venta PRIMARY KEY (id_detalle_venta),

    CONSTRAINT fk_detalle_venta_venta
        FOREIGN KEY (id_venta)
        REFERENCES venta(id_venta),

    CONSTRAINT fk_detalle_venta_producto
        FOREIGN KEY (id_producto)
        REFERENCES producto(id_producto)

) ENGINE=InnoDB;

-- ==========================================================
-- TABLA: sucursal
-- ==========================================================

CREATE TABLE sucursal (

    id_sucursal INT UNSIGNED AUTO_INCREMENT,

    nombre VARCHAR(100) NOT NULL,

    direccion VARCHAR(255) NOT NULL,

    telefono VARCHAR(20),

    encargado VARCHAR(100),

    estado BOOLEAN NOT NULL DEFAULT TRUE,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_sucursal PRIMARY KEY (id_sucursal),

    CONSTRAINT uk_sucursal_nombre UNIQUE (nombre)

) ENGINE=InnoDB;

-- ==========================================================
-- TABLA: metodo_pago
-- ==========================================================

CREATE TABLE metodo_pago (

    id_metodo_pago INT UNSIGNED AUTO_INCREMENT,

    nombre VARCHAR(100) NOT NULL,

    descripcion VARCHAR(255),

    estado BOOLEAN NOT NULL DEFAULT TRUE,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_metodo_pago PRIMARY KEY (id_metodo_pago),

    CONSTRAINT uk_metodo_pago_nombre UNIQUE (nombre)

) ENGINE=InnoDB;

-- ==========================================================
-- TABLA: apertura_caja
-- ==========================================================

CREATE TABLE apertura_caja (

    id_apertura INT UNSIGNED AUTO_INCREMENT,

    id_caja INT UNSIGNED NOT NULL,

    id_usuario INT UNSIGNED NOT NULL,

    fecha_apertura DATETIME NOT NULL,

    monto_inicial DECIMAL(12,2) NOT NULL,

    observaciones VARCHAR(255),

    estado BOOLEAN NOT NULL DEFAULT TRUE,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_apertura_caja PRIMARY KEY (id_apertura),

    CONSTRAINT fk_apertura_caja
        FOREIGN KEY (id_caja)
        REFERENCES caja(id_caja),

    CONSTRAINT fk_apertura_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)

) ENGINE=InnoDB;

-- ==========================================================
-- TABLA: cierre_caja
-- ==========================================================

CREATE TABLE cierre_caja (

    id_cierre INT UNSIGNED AUTO_INCREMENT,

    id_apertura INT UNSIGNED NOT NULL,

    id_usuario INT UNSIGNED NOT NULL,

    fecha_cierre DATETIME NOT NULL,

    monto_inicial DECIMAL(12,2) NOT NULL,

    monto_final DECIMAL(12,2) NOT NULL,

    diferencia DECIMAL(12,2) NOT NULL DEFAULT 0,

    observaciones VARCHAR(255),

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_cierre_caja PRIMARY KEY (id_cierre),

    CONSTRAINT fk_cierre_apertura
        FOREIGN KEY (id_apertura)
        REFERENCES apertura_caja(id_apertura),

    CONSTRAINT fk_cierre_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)

) ENGINE=InnoDB;

-- ==========================================================
-- TABLA: merma
-- ==========================================================

CREATE TABLE merma (

    id_merma INT UNSIGNED AUTO_INCREMENT,

    id_producto INT UNSIGNED NOT NULL,

    id_usuario INT UNSIGNED NOT NULL,

    cantidad INT NOT NULL,

    motivo VARCHAR(255) NOT NULL,

    fecha DATETIME NOT NULL,

    observaciones VARCHAR(255),

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_merma PRIMARY KEY (id_merma),

    CONSTRAINT fk_merma_producto
        FOREIGN KEY (id_producto)
        REFERENCES producto(id_producto),

    CONSTRAINT fk_merma_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)

) ENGINE=InnoDB;

-- ==========================================================
-- TABLA: ajuste
-- ==========================================================

CREATE TABLE ajuste (

    id_ajuste INT UNSIGNED AUTO_INCREMENT,

    id_producto INT UNSIGNED NOT NULL,

    id_usuario INT UNSIGNED NOT NULL,

    cantidad INT NOT NULL,

    tipo ENUM('ENTRADA','SALIDA') NOT NULL,

    motivo VARCHAR(255) NOT NULL,

    fecha DATETIME NOT NULL,

    observaciones VARCHAR(255),

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_ajuste PRIMARY KEY (id_ajuste),

    CONSTRAINT fk_ajuste_producto
        FOREIGN KEY (id_producto)
        REFERENCES producto(id_producto),

    CONSTRAINT fk_ajuste_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)

) ENGINE=InnoDB;


-- ==========================================================
-- TABLA: configuracion_tributaria
-- ==========================================================

CREATE TABLE configuracion_tributaria (

    id_configuracion_tributaria INT UNSIGNED AUTO_INCREMENT,

    nombre VARCHAR(100) NOT NULL,

    descripcion VARCHAR(255),

    porcentaje DECIMAL(5,2) NOT NULL,

    aplica_compras BOOLEAN NOT NULL DEFAULT TRUE,

    aplica_ventas BOOLEAN NOT NULL DEFAULT TRUE,

    estado BOOLEAN NOT NULL DEFAULT TRUE,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_configuracion_tributaria
        PRIMARY KEY (id_configuracion_tributaria),

    CONSTRAINT uk_configuracion_tributaria_nombre
        UNIQUE (nombre)

) ENGINE=InnoDB;

-- ==========================================================
-- TABLA: gasto_operativo
-- ==========================================================

CREATE TABLE gasto_operativo (

    id_gasto INT UNSIGNED AUTO_INCREMENT,

    id_sucursal INT UNSIGNED NOT NULL,

    id_usuario INT UNSIGNED NOT NULL,

    id_caja INT UNSIGNED NULL,

    descripcion VARCHAR(255) NOT NULL,

    categoria VARCHAR(100) NOT NULL,

    monto DECIMAL(12,2) NOT NULL,

    fecha_gasto DATETIME NOT NULL,

    observaciones VARCHAR(255),

    estado BOOLEAN NOT NULL DEFAULT TRUE,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT pk_gasto_operativo
        PRIMARY KEY (id_gasto),

    CONSTRAINT fk_gasto_sucursal
        FOREIGN KEY (id_sucursal)
        REFERENCES sucursal(id_sucursal),

    CONSTRAINT fk_gasto_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario),

    CONSTRAINT fk_gasto_caja
        FOREIGN KEY (id_caja)
        REFERENCES caja(id_caja)

) ENGINE=InnoDB;


-- ==========================================================
-- TABLA: log_acciones
-- ==========================================================

CREATE TABLE log_acciones (

    id_log INT UNSIGNED AUTO_INCREMENT,

    id_usuario INT UNSIGNED NOT NULL,

    id_modulo INT UNSIGNED NOT NULL,

    tipo_accion ENUM(
        'LOGIN',
        'LOGOUT',
        'CREAR',
        'MODIFICAR',
        'ELIMINAR',
        'CONSULTAR',
        'EXPORTAR',
        'IMPORTAR',
        'ERROR'
    ) NOT NULL,

    descripcion VARCHAR(500) NOT NULL,

    ip_origen VARCHAR(45),

    navegador VARCHAR(150),

    fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_log_acciones
        PRIMARY KEY (id_log),

    CONSTRAINT fk_log_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario),

    CONSTRAINT fk_log_modulo
        FOREIGN KEY (id_modulo)
        REFERENCES modulo(id_modulo)

) ENGINE=InnoDB;