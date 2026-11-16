-- =============================================================================
-- SALÓN & SPA ALEIDA - DDL & DML SCHEMA PARA POSTGRESQL (RENDER DATABASE)
-- Compatible con PostgreSQL 15/16 en Render
-- =============================================================================

-- 1. TABLA: CLIENTES Y FICHAS ESTÉTICAS (CU02 - RF01)
CREATE TABLE IF NOT EXISTS clientes (
    dni VARCHAR(15) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(25),
    preferencias TEXT,
    visitas INTEGER DEFAULT 1,
    ultima_visita VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABLA: CATÁLOGO DE SERVICIOS Y TRATAMIENTOS (CU07 - RF10)
CREATE TABLE IF NOT EXISTS servicios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    categoria VARCHAR(60) NOT NULL,
    duracion INTEGER NOT NULL,
    precio NUMERIC(10,2) NOT NULL,
    comision INTEGER DEFAULT 25,
    activo BOOLEAN DEFAULT TRUE
);

-- 3. TABLA: PRODUCTOS E INSUMOS CRÍTICOS (CU06 - RF09)
CREATE TABLE IF NOT EXISTS productos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    proveedor VARCHAR(120) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    stock_min INTEGER NOT NULL DEFAULT 5,
    costo NUMERIC(10,2) NOT NULL DEFAULT 0.0,
    precio_venta NUMERIC(10,2) NOT NULL DEFAULT 0.0,
    alerta BOOLEAN DEFAULT FALSE
);

-- 4. TABLA: CITAS Y AGENDA (CU01 - RF02, RF03)
CREATE TABLE IF NOT EXISTS citas (
    id SERIAL PRIMARY KEY,
    hora VARCHAR(20) NOT NULL,
    fecha VARCHAR(20) NOT NULL,
    cliente VARCHAR(100) NOT NULL,
    dni VARCHAR(15) NOT NULL,
    servicio VARCHAR(120) NOT NULL,
    especialista VARCHAR(100) NOT NULL,
    estado VARCHAR(30) DEFAULT 'Confirmada',
    monto NUMERIC(10,2) DEFAULT 0.0,
    cobrado BOOLEAN DEFAULT FALSE,
    motivo_cancelacion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice de no-colisión para optimizar consultas de disponibilidad
CREATE INDEX IF NOT EXISTS idx_citas_agenda ON citas (fecha, hora, especialista);

-- 5. TABLA: VENTAS Y BOLETAS ELECTRÓNICAS (CU03 - RF04, RF05)
CREATE TABLE IF NOT EXISTS ventas (
    id SERIAL PRIMARY KEY,
    numero_boleta VARCHAR(30) UNIQUE NOT NULL,
    fecha VARCHAR(30) NOT NULL,
    cliente VARCHAR(100) NOT NULL,
    servicio VARCHAR(120) NOT NULL,
    subtotal NUMERIC(10,2) NOT NULL,
    igv NUMERIC(10,2) NOT NULL,
    descuento NUMERIC(10,2) DEFAULT 0.0,
    total NUMERIC(10,2) NOT NULL,
    medio_pago VARCHAR(40) NOT NULL,
    estado VARCHAR(25) DEFAULT 'Emitida',
    nota_credito VARCHAR(30)
);

-- 6. TABLA: NOTAS DE CRÉDITO Y ANULACIONES (CU04 - RF06)
CREATE TABLE IF NOT EXISTS anulaciones (
    id SERIAL PRIMARY KEY,
    fecha VARCHAR(30) NOT NULL,
    boleta VARCHAR(30) NOT NULL,
    nota_credito VARCHAR(30) NOT NULL,
    monto NUMERIC(10,2) NOT NULL,
    motivo TEXT NOT NULL,
    autorizado_por VARCHAR(100) NOT NULL
);

-- 7. TABLA: CONTROL DE CAJA Y ARQUEO DIARIO (CU05 - RF07, RF08)
CREATE TABLE IF NOT EXISTS caja (
    id SERIAL PRIMARY KEY,
    fecha VARCHAR(20) NOT NULL,
    apertura NUMERIC(10,2) DEFAULT 150.0,
    efectivo NUMERIC(10,2) DEFAULT 0.0,
    digital NUMERIC(10,2) DEFAULT 0.0,
    egresos NUMERIC(10,2) DEFAULT 0.0,
    saldo_teorico NUMERIC(10,2) DEFAULT 150.0,
    arqueo_fisico NUMERIC(10,2),
    diferencia NUMERIC(10,2),
    estado VARCHAR(20) DEFAULT 'Abierta',
    turno VARCHAR(30) DEFAULT 'Turno Mañana'
);

-- 8. TABLA: MOVIMIENTOS DETALLADOS DE CAJA
CREATE TABLE IF NOT EXISTS caja_movimientos (
    id SERIAL PRIMARY KEY,
    hora VARCHAR(20) NOT NULL,
    tipo VARCHAR(30) NOT NULL,
    monto NUMERIC(10,2) NOT NULL,
    detalle TEXT NOT NULL
);

-- 9. TABLA: ÓRDENES DE COMPRA (CU06 - RF09)
CREATE TABLE IF NOT EXISTS compras (
    id SERIAL PRIMARY KEY,
    numero_oc VARCHAR(30) UNIQUE NOT NULL,
    fecha VARCHAR(20) NOT NULL,
    proveedor VARCHAR(120) NOT NULL,
    insumo VARCHAR(150) NOT NULL,
    cantidad INTEGER NOT NULL,
    monto_total NUMERIC(10,2) NOT NULL,
    estado VARCHAR(30) DEFAULT 'En Tránsito'
);

-- 10. TABLA: USUARIOS Y ROLES (CU08 - RF11)
CREATE TABLE IF NOT EXISTS usuarios (
    usuario VARCHAR(50) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    rol VARCHAR(50) NOT NULL,
    permisos TEXT NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);

-- =============================================================================
-- INSERCIÓN DE DATOS SEMILLA (SEED DATA)
-- =============================================================================

INSERT INTO clientes (dni, nombre, telefono, preferencias, visitas, ultima_visita) VALUES
('72819382', 'Mariana Torres', '987654321', 'Piel mixta, prefiere aromaterapia de lavanda.', 12, '2026-10-06'),
('45910284', 'Patricia Valdivia', '945112233', 'Sensibilidad a tintes con amoníaco.', 8, '2026-10-06'),
('48192039', 'Claudia Morales', '912345678', 'Tratamiento keratina semestral.', 5, '2026-10-06'),
('70829104', 'Jessica Rivas', '923456789', 'Manicura semipermanente color nude.', 3, '2026-10-05')
ON CONFLICT (dni) DO NOTHING;

INSERT INTO servicios (nombre, categoria, duracion, precio, comision, activo) VALUES
('Masaje Relajante Aleida', 'Spa & Bienestar', 90, 280.0, 25, TRUE),
('Facial Rejuvenecedor con Oro', 'Cosmiatría Facial', 75, 450.0, 30, TRUE),
('Tratamiento Capilar Keratina', 'Cuidado Capilar', 120, 350.0, 30, TRUE),
('Manicura Spa Premium', 'Manos & Pies', 60, 150.0, 35, TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO productos (nombre, proveedor, stock, stock_min, costo, precio_venta, alerta) VALUES
('Tinte Profesional 6.1 (Cenizo)', 'L''Oréal Professionnel Perú', 2, 6, 28.0, 45.0, TRUE),
('Crema Nutritiva Keratina 1L', 'Distribuidora Belleza Total SAC', 1, 4, 85.0, 130.0, TRUE),
('Aceite de Argán Puro 250ml', 'BioCosmetics Natura', 8, 3, 35.0, 60.0, FALSE)
ON CONFLICT DO NOTHING;

INSERT INTO citas (hora, fecha, cliente, dni, servicio, especialista, estado, monto, cobrado) VALUES
('09:00 AM', '2026-10-06', 'Mariana Torres', '72819382', 'Masaje Relajante Aleida', 'Carmen Sánchez', 'Atendida', 280.0, TRUE),
('10:30 AM', '2026-10-06', 'Patricia Valdivia', '45910284', 'Facial Rejuvenecedor con Oro', 'Carmen Sánchez', 'Confirmada', 450.0, FALSE),
('11:45 AM', '2026-10-06', 'Claudia Morales', '48192039', 'Tratamiento Capilar Keratina', 'Luisa Paredes', 'En Atención', 350.0, FALSE),
('02:30 PM', '2026-10-06', 'Jessica Rivas', '70829104', 'Manicura Spa Premium', 'Ana Vargas', 'Pendiente', 150.0, FALSE)
ON CONFLICT DO NOTHING;

INSERT INTO ventas (numero_boleta, fecha, cliente, servicio, subtotal, igv, descuento, total, medio_pago, estado) VALUES
('B001-0004820', '2026-10-06 09:45', 'Mariana Torres', 'Masaje Relajante Aleida', 237.29, 42.71, 0.0, 280.0, 'Efectivo', 'Emitida')
ON CONFLICT (numero_boleta) DO NOTHING;

INSERT INTO anulaciones (fecha, boleta, nota_credito, monto, motivo, autorizado_por) VALUES
('2026-10-05 16:30', 'B001-0004810', 'NC-012', 120.0, 'Devolución por insatisfacción', 'Aleida Mendoza (Gerente)')
ON CONFLICT DO NOTHING;

INSERT INTO caja (fecha, apertura, efectivo, digital, egresos, saldo_teorico, estado, turno) VALUES
('2026-10-06', 150.0, 720.0, 1580.0, 45.0, 2405.0, 'Abierta', 'Turno Mañana')
ON CONFLICT DO NOTHING;

INSERT INTO caja_movimientos (hora, tipo, monto, detalle) VALUES
('08:30 AM', 'Apertura', 150.0, 'Fondo de sencillo inicial (RF07)'),
('09:45 AM', 'Ingreso', 280.0, 'Cobro Boleta B001-4820 en Efectivo (RF05)'),
('11:00 AM', 'Egreso', -45.0, 'Salida menor por refrigerio de colaboradores (RF07)'),
('11:30 AM', 'Ingreso', 450.0, 'Cobro Boleta B001-4821 vía Yape (RF05)'),
('01:15 PM', 'Ingreso', 350.0, 'Cobro Boleta B001-4822 con Tarjeta POS (RF05)')
ON CONFLICT DO NOTHING;

INSERT INTO compras (numero_oc, fecha, proveedor, insumo, cantidad, monto_total, estado) VALUES
('OC-2026-088', '2026-10-05', 'L''Oréal Professionnel Perú', 'Tinte Profesional 6.1 (12 unidades)', 12, 336.0, 'En Tránsito')
ON CONFLICT (numero_oc) DO NOTHING;

INSERT INTO usuarios (usuario, nombre, rol, permisos) VALUES
('cramos', 'Camila Ramos', 'Recepcionista', 'Agenda (CU01), Clientes (CU02), POS (CU03)'),
('aleida_admin', 'Aleida Mendoza', 'Gerente General', 'Acceso Total (CU01-CU09), Aprobación de Anulaciones (CU04)'),
('csanchez', 'Carmen Sánchez', 'Terapeuta / Cosmiatra', 'Consulta de Agenda propia, Historial de atenciones')
ON CONFLICT (usuario) DO NOTHING;
