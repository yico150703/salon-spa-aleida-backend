-- =============================================================================
-- SALÓN & SPA ALEIDA S.A.C. - SCHEMA OFICIAL CANÓNICO (11 TABLAS)
-- Nombres exactos de Clases de Rational Rose (CamelCase)
-- Base de Datos PostgreSQL (Render) & SQLite (Local)
-- =============================================================================

-- 1. TABLA: "Cliente" (Clase Rational Rose: Cliente)
CREATE TABLE IF NOT EXISTS "Cliente" (
    dni VARCHAR(15) PRIMARY KEY,
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) NOT NULL DEFAULT '',
    telefono VARCHAR(25),
    direccion VARCHAR(150) DEFAULT 'Lima, Perú',
    preferencias TEXT,
    fecharegistro VARCHAR(30) DEFAULT '2026-10-06',
    estadopadron VARCHAR(30) DEFAULT 'Activo',
    correo VARCHAR(100) DEFAULT ''
);

-- 2. TABLA: "FichaEstetica" (Clase Rational Rose: FichaEstetica)
CREATE TABLE IF NOT EXISTS "FichaEstetica" (
    codigficha VARCHAR(30) PRIMARY KEY,
    dni_cliente VARCHAR(15) NOT NULL REFERENCES "Cliente"(dni) ON DELETE CASCADE,
    tipopiel VARCHAR(50) DEFAULT 'Mixta',
    alergias TEXT DEFAULT 'Ninguna',
    tratamientosprevios TEXT DEFAULT 'Ninguno',
    condicionesmedicas TEXT DEFAULT 'Ninguna',
    diagnosticoinicial TEXT DEFAULT 'Apto para tratamientos',
    fechacreacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. TABLA: "Cita" (Clase Rational Rose: Cita)
CREATE TABLE IF NOT EXISTS "Cita" (
    codigcita VARCHAR(30) PRIMARY KEY,
    codigreserva VARCHAR(30) NOT NULL,
    fecha VARCHAR(20) NOT NULL,
    horainicio VARCHAR(20) NOT NULL,
    horafin VARCHAR(20) DEFAULT '10:30 AM',
    dni_cliente VARCHAR(15) NOT NULL REFERENCES "Cliente"(dni) ON DELETE CASCADE,
    especialista VARCHAR(100) NOT NULL,
    cabina VARCHAR(60) DEFAULT 'Cabina Estándar',
    montototal NUMERIC(10,2) DEFAULT 0.0,
    estado VARCHAR(30) DEFAULT 'Confirmada',
    motivocancelacion TEXT DEFAULT '',
    observaciones TEXT DEFAULT ''
);

-- 4. TABLA: "Servicio" (Clase Rational Rose: Servicio)
CREATE TABLE IF NOT EXISTS "Servicio" (
    codigservicio VARCHAR(30) PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    categoria VARCHAR(60) NOT NULL,
    preciobase NUMERIC(10,2) NOT NULL,
    duracionminutos INTEGER NOT NULL,
    cabinarequerida VARCHAR(60) DEFAULT 'Cabina Estándar',
    porcentajecomision NUMERIC(5,2) DEFAULT 25.0,
    estadoactivo BOOLEAN DEFAULT TRUE
);

-- 5. TABLA: "Promocion" (Clase Rational Rose: Promocion)
CREATE TABLE IF NOT EXISTS "Promocion" (
    codigpromocion VARCHAR(30) PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    porcentajedescuento NUMERIC(5,2) DEFAULT 0.0,
    montodescuento NUMERIC(10,2) DEFAULT 0.0,
    fechainicio VARCHAR(20) NOT NULL,
    fechafin VARCHAR(20) NOT NULL,
    condiciones TEXT DEFAULT 'Válido días hábiles',
    estado VARCHAR(20) DEFAULT 'Vigente'
);

-- 6. TABLA: "VentaComprobante" (Clase Rational Rose: VentaComprobante)
CREATE TABLE IF NOT EXISTS "VentaComprobante" (
    numerocomprobante VARCHAR(30) PRIMARY KEY,
    tipocomprobante VARCHAR(40) DEFAULT 'Boleta de Venta',
    serie VARCHAR(10) DEFAULT 'B001',
    fechaemision VARCHAR(30) NOT NULL,
    horaemision VARCHAR(20) DEFAULT '09:45 AM',
    dni_cliente VARCHAR(15) REFERENCES "Cliente"(dni),
    subtotal NUMERIC(10,2) NOT NULL,
    igv NUMERIC(10,2) NOT NULL,
    descuentototal NUMERIC(10,2) DEFAULT 0.0,
    totalneto NUMERIC(10,2) NOT NULL,
    estadocomprobante VARCHAR(25) DEFAULT 'Emitida',
    notacredito VARCHAR(30)
);

-- 7. TABLA: "DetalleComprobante" (Clase Rational Rose: DetalleComprobante)
CREATE TABLE IF NOT EXISTS "DetalleComprobante" (
    item SERIAL PRIMARY KEY,
    numerocomprobante VARCHAR(30) NOT NULL REFERENCES "VentaComprobante"(numerocomprobante) ON DELETE CASCADE,
    codigitem VARCHAR(30) NOT NULL,
    tipoitem VARCHAR(30) DEFAULT 'Servicio',
    descripcion TEXT NOT NULL,
    cantidad INTEGER NOT NULL DEFAULT 1,
    preciounitario NUMERIC(10,2) NOT NULL,
    subtotal NUMERIC(10,2) NOT NULL
);

-- 8. TABLA: "Pago" (Clase Rational Rose: Pago)
CREATE TABLE IF NOT EXISTS "Pago" (
    codigpago VARCHAR(30) PRIMARY KEY,
    numerocomprobante VARCHAR(30) NOT NULL REFERENCES "VentaComprobante"(numerocomprobante) ON DELETE CASCADE,
    monto NUMERIC(10,2) NOT NULL,
    mediopago VARCHAR(40) NOT NULL,
    referenciaoperacion VARCHAR(60),
    fechahora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(25) DEFAULT 'Aprobado'
);

-- 9. TABLA: "CajaSesion" (Clase Rational Rose: CajaSesion)
CREATE TABLE IF NOT EXISTS "CajaSesion" (
    codigsesion VARCHAR(30) PRIMARY KEY,
    cajero VARCHAR(100) NOT NULL,
    turno VARCHAR(30) NOT NULL,
    montoapertura NUMERIC(10,2) DEFAULT 150.0,
    fechahoraapertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    montocierresistema NUMERIC(10,2) DEFAULT 150.0,
    montocierrereal NUMERIC(10,2),
    diferencia NUMERIC(10,2),
    estadosesion VARCHAR(20) DEFAULT 'Abierta'
);

-- 10. TABLA: "MovimientoCaja" (Clase Rational Rose: MovimientoCaja)
CREATE TABLE IF NOT EXISTS "MovimientoCaja" (
    codigmovimiento VARCHAR(30) PRIMARY KEY,
    codigsesion VARCHAR(30) NOT NULL REFERENCES "CajaSesion"(codigsesion) ON DELETE CASCADE,
    tipomovimiento VARCHAR(30) NOT NULL,
    concepto TEXT NOT NULL,
    monto NUMERIC(10,2) NOT NULL,
    fechahora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    autorizadopor VARCHAR(100) DEFAULT 'Administrador'
);

-- 11. TABLA: "Usuario" (Clase Rational Rose: Usuario)
CREATE TABLE IF NOT EXISTS "Usuario" (
    username VARCHAR(50) PRIMARY KEY,
    codigusuario VARCHAR(30) DEFAULT 'USR-001',
    passwordhash VARCHAR(100) DEFAULT '1234',
    nombres VARCHAR(100) NOT NULL,
    apellidos VARCHAR(100) DEFAULT '',
    dni VARCHAR(15),
    rol VARCHAR(50) NOT NULL,
    turno VARCHAR(50) DEFAULT 'Turno Mañana',
    celular VARCHAR(25),
    email VARCHAR(100),
    estado BOOLEAN DEFAULT TRUE
);

-- VISTA SINÓNIMA: "VentasComprobante"
CREATE OR REPLACE VIEW "VentasComprobante" AS 
SELECT * FROM "VentaComprobante";
