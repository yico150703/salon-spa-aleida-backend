"""
=============================================================================
CAPA DE BASE DE DATOS - CONECTOR POSTGRESQL & SQLITE (RENDER & LOCAL)
Soporta despliegue nativo en Render PostgreSQL (DATABASE_URL)
Con fallback transparente a SQLite para desarrollo local sin dependencias externas.
=============================================================================
"""

import os
import sqlite3
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

logger = logging.getLogger("spa_database")
logging.basicConfig(level=logging.INFO)

DATABASE_URL = os.environ.get("DATABASE_URL")

# Si Render provee postgres:// lo adaptamos para compatibilidad
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

_pg_pool = None

class _PooledConnWrapper:
    def __init__(self, raw_conn, pool):
        self._conn = raw_conn
        self._pool = pool

    def close(self):
        if self._pool and self._conn:
            try:
                self._pool.putconn(self._conn)
            except Exception:
                pass
            self._conn = None

    def __getattr__(self, item):
        return getattr(self._conn, item)

def is_postgres():
    return bool(DATABASE_URL)

def get_connection():
    """Retorna una conexión activa a PostgreSQL (en Render con Connection Pool) o SQLite (en local)."""
    global _pg_pool
    if is_postgres():
        import psycopg2
        import psycopg2.pool
        if _pg_pool is None:
            sslmode = os.environ.get("PGSSLMODE", "require") if "render.com" in DATABASE_URL else "prefer"
            _pg_pool = psycopg2.pool.ThreadedConnectionPool(1, 10, DATABASE_URL, sslmode=sslmode)
        try:
            raw_conn = _pg_pool.getconn()
            raw_conn.autocommit = True
            return _PooledConnWrapper(raw_conn, _pg_pool)
        except Exception:
            sslmode = os.environ.get("PGSSLMODE", "require") if "render.com" in DATABASE_URL else "prefer"
            conn = psycopg2.connect(DATABASE_URL, sslmode=sslmode)
            conn.autocommit = True
            return conn
    else:
        db_path = os.path.join(os.path.dirname(__file__), "spa_aleida.db")
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

def get_cursor(conn):
    """Devuelve un cursor configurado con retorno tipo diccionario."""
    if is_postgres():
        import psycopg2.extras
        return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    else:
        return conn.cursor()

def init_db():
    """Crea las tablas en PostgreSQL / SQLite y carga los datos maestros iniciales."""
    conn = get_connection()
    cur = get_cursor(conn)
    
    postgres_mode = is_postgres()
    id_pk = "SERIAL PRIMARY KEY" if postgres_mode else "INTEGER PRIMARY KEY AUTOINCREMENT"
    
    # 1. Tabla Clientes
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS clientes (
        dni VARCHAR(15) PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        telefono VARCHAR(25),
        preferencias TEXT,
        visitas INTEGER DEFAULT 1,
        ultima_visita VARCHAR(20),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Tabla Servicios (Catálogo)
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS servicios (
        id {id_pk},
        nombre VARCHAR(120) NOT NULL,
        categoria VARCHAR(60) NOT NULL,
        duracion INTEGER NOT NULL,
        precio NUMERIC(10,2) NOT NULL,
        comision INTEGER DEFAULT 25,
        activo BOOLEAN DEFAULT TRUE
    );
    """)

    # 3. Tabla Insumos / Productos
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS productos (
        id {id_pk},
        nombre VARCHAR(150) NOT NULL,
        proveedor VARCHAR(120) NOT NULL,
        stock INTEGER NOT NULL DEFAULT 0,
        stock_min INTEGER NOT NULL DEFAULT 5,
        costo NUMERIC(10,2) NOT NULL DEFAULT 0.0,
        precio_venta NUMERIC(10,2) NOT NULL DEFAULT 0.0,
        alerta BOOLEAN DEFAULT FALSE
    );
    """)

    # 4. Tabla Citas
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS citas (
        id {id_pk},
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
    """)

    # 5. Tabla Ventas (Boletas Electrónicas con IGV 18%)
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS ventas (
        id {id_pk},
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
    """)

    # 6. Tabla Anulaciones / Notas de Crédito
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS anulaciones (
        id {id_pk},
        fecha VARCHAR(30) NOT NULL,
        boleta VARCHAR(30) NOT NULL,
        nota_credito VARCHAR(30) NOT NULL,
        monto NUMERIC(10,2) NOT NULL,
        motivo TEXT NOT NULL,
        autorizado_por VARCHAR(100) NOT NULL
    );
    """)

    # 7. Tabla Caja
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS caja (
        id {id_pk},
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
    """)

    # 8. Tabla Movimientos de Caja
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS caja_movimientos (
        id {id_pk},
        hora VARCHAR(20) NOT NULL,
        tipo VARCHAR(30) NOT NULL,
        monto NUMERIC(10,2) NOT NULL,
        detalle TEXT NOT NULL
    );
    """)

    # 9. Tabla Órdenes de Compra
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS compras (
        id {id_pk},
        numero_oc VARCHAR(30) UNIQUE NOT NULL,
        fecha VARCHAR(20) NOT NULL,
        proveedor VARCHAR(120) NOT NULL,
        insumo VARCHAR(150) NOT NULL,
        cantidad INTEGER NOT NULL,
        monto_total NUMERIC(10,2) NOT NULL,
        estado VARCHAR(30) DEFAULT 'En Tránsito'
    );
    """)

    # 10. Tabla Usuarios del Sistema
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS usuarios (
        usuario VARCHAR(50) PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        rol VARCHAR(50) NOT NULL,
        permisos TEXT NOT NULL,
        activo BOOLEAN DEFAULT TRUE
    );
    """)

    if not postgres_mode:
        conn.commit()

    # Sembrar datos maestros si las tablas están vacías
    seed_initial_data(conn, cur, postgres_mode)
    conn.close()
    logger.info("Base de datos inicializada correctamente en modo: %s", "PostgreSQL (Render)" if postgres_mode else "SQLite (Local)")

def seed_initial_data(conn, cur, postgres_mode):
    """Puebla las tablas con los registros canónicos del Modelo Spa Aleida."""
    # Clientes
    cur.execute("SELECT COUNT(*) AS c FROM clientes;")
    row = cur.fetchone()
    count = row['c'] if isinstance(row, dict) else row[0]
    if count == 0:
        clientes = [
            ("72819382", "Mariana Torres", "987654321", "Piel mixta, prefiere aromaterapia de lavanda.", 12, "2026-10-06"),
            ("45910284", "Patricia Valdivia", "945112233", "Sensibilidad a tintes con amoníaco.", 8, "2026-10-06"),
            ("48192039", "Claudia Morales", "912345678", "Tratamiento keratina semestral.", 5, "2026-10-06"),
            ("70829104", "Jessica Rivas", "923456789", "Manicura semipermanente color nude.", 3, "2026-10-05")
        ]
        ph = "%s, %s, %s, %s, %s, %s" if postgres_mode else "?, ?, ?, ?, ?, ?"
        for c in clientes:
            cur.execute(f"INSERT INTO clientes (dni, nombre, telefono, preferencias, visitas, ultima_visita) VALUES ({ph})", c)

    # Servicios
    cur.execute("SELECT COUNT(*) AS c FROM servicios;")
    row = cur.fetchone()
    count = row['c'] if isinstance(row, dict) else row[0]
    if count == 0:
        servicios = [
            ("Masaje Relajante Aleida", "Spa & Bienestar", 90, 280.0, 25, True),
            ("Facial Rejuvenecedor con Oro", "Cosmiatría Facial", 75, 450.0, 30, True),
            ("Tratamiento Capilar Keratina", "Cuidado Capilar", 120, 350.0, 30, True),
            ("Manicura Spa Premium", "Manos & Pies", 60, 150.0, 35, True)
        ]
        ph = "%s, %s, %s, %s, %s, %s" if postgres_mode else "?, ?, ?, ?, ?, ?"
        for s in servicios:
            cur.execute(f"INSERT INTO servicios (nombre, categoria, duracion, precio, comision, activo) VALUES ({ph})", s)

    # Productos
    cur.execute("SELECT COUNT(*) AS c FROM productos;")
    row = cur.fetchone()
    count = row['c'] if isinstance(row, dict) else row[0]
    if count == 0:
        productos = [
            ("Tinte Profesional 6.1 (Cenizo)", "L'Oréal Professionnel Perú", 2, 6, 28.0, 45.0, True),
            ("Crema Nutritiva Keratina 1L", "Distribuidora Belleza Total SAC", 1, 4, 85.0, 130.0, True),
            ("Aceite de Argán Puro 250ml", "BioCosmetics Natura", 8, 3, 35.0, 60.0, False)
        ]
        ph = "%s, %s, %s, %s, %s, %s, %s" if postgres_mode else "?, ?, ?, ?, ?, ?, ?"
        for p in productos:
            cur.execute(f"INSERT INTO productos (nombre, proveedor, stock, stock_min, costo, precio_venta, alerta) VALUES ({ph})", p)

    # Citas
    cur.execute("SELECT COUNT(*) AS c FROM citas;")
    row = cur.fetchone()
    count = row['c'] if isinstance(row, dict) else row[0]
    if count == 0:
        citas = [
            ("09:00 AM", "2026-10-06", "Mariana Torres", "72819382", "Masaje Relajante Aleida", "Carmen Sánchez", "Atendida", 280.0, True, None),
            ("10:30 AM", "2026-10-06", "Patricia Valdivia", "45910284", "Facial Rejuvenecedor con Oro", "Carmen Sánchez", "Confirmada", 450.0, False, None),
            ("11:45 AM", "2026-10-06", "Claudia Morales", "48192039", "Tratamiento Capilar Keratina", "Luisa Paredes", "En Atención", 350.0, False, None),
            ("02:30 PM", "2026-10-06", "Jessica Rivas", "70829104", "Manicura Spa Premium", "Ana Vargas", "Pendiente", 150.0, False, None)
        ]
        ph = "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s" if postgres_mode else "?, ?, ?, ?, ?, ?, ?, ?, ?, ?"
        for ci in citas:
            cur.execute(f"INSERT INTO citas (hora, fecha, cliente, dni, servicio, especialista, estado, monto, cobrado, motivo_cancelacion) VALUES ({ph})", ci)

    # Ventas
    cur.execute("SELECT COUNT(*) AS c FROM ventas;")
    row = cur.fetchone()
    count = row['c'] if isinstance(row, dict) else row[0]
    if count == 0:
        ventas = [
            ("B001-0004820", "2026-10-06 09:45", "Mariana Torres", "Masaje Relajante Aleida", 237.29, 42.71, 0.0, 280.0, "Efectivo", "Emitida", None)
        ]
        ph = "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" if postgres_mode else "?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?"
        for v in ventas:
            cur.execute(f"INSERT INTO ventas (numero_boleta, fecha, cliente, servicio, subtotal, igv, descuento, total, medio_pago, estado, nota_credito) VALUES ({ph})", v)

    # Anulaciones
    cur.execute("SELECT COUNT(*) AS c FROM anulaciones;")
    row = cur.fetchone()
    count = row['c'] if isinstance(row, dict) else row[0]
    if count == 0:
        anulaciones = [
            ("2026-10-05 16:30", "B001-0004810", "NC-012", 120.0, "Devolución por insatisfacción", "Aleida Mendoza (Gerente)")
        ]
        ph = "%s, %s, %s, %s, %s, %s" if postgres_mode else "?, ?, ?, ?, ?, ?"
        for a in anulaciones:
            cur.execute(f"INSERT INTO anulaciones (fecha, boleta, nota_credito, monto, motivo, autorizado_por) VALUES ({ph})", a)

    # Caja y Movimientos
    cur.execute("SELECT COUNT(*) AS c FROM caja;")
    row = cur.fetchone()
    count = row['c'] if isinstance(row, dict) else row[0]
    if count == 0:
        cur.execute(
            f"INSERT INTO caja (fecha, apertura, efectivo, digital, egresos, saldo_teorico, estado, turno) "
            f"VALUES ({'%s, %s, %s, %s, %s, %s, %s, %s' if postgres_mode else '?, ?, ?, ?, ?, ?, ?, ?'})",
            ("2026-10-06", 150.0, 720.0, 1580.0, 45.0, 2405.0, "Abierta", "Turno Mañana")
        )
        movimientos = [
            ("08:30 AM", "Apertura", 150.0, "Fondo de sencillo inicial (RF07)"),
            ("09:45 AM", "Ingreso", 280.0, "Cobro Boleta B001-4820 en Efectivo (RF05)"),
            ("11:00 AM", "Egreso", -45.0, "Salida menor por refrigerio de colaboradores (RF07)"),
            ("11:30 AM", "Ingreso", 450.0, "Cobro Boleta B001-4821 vía Yape (RF05)"),
            ("01:15 PM", "Ingreso", 350.0, "Cobro Boleta B001-4822 con Tarjeta POS (RF05)")
        ]
        ph = "%s, %s, %s, %s" if postgres_mode else "?, ?, ?, ?"
        for m in movimientos:
            cur.execute(f"INSERT INTO caja_movimientos (hora, tipo, monto, detalle) VALUES ({ph})", m)

    # Compras
    cur.execute("SELECT COUNT(*) AS c FROM compras;")
    row = cur.fetchone()
    count = row['c'] if isinstance(row, dict) else row[0]
    if count == 0:
        compras = [
            ("OC-2026-088", "2026-10-05", "L'Oréal Professionnel Perú", "Tinte Profesional 6.1 (12 unidades)", 12, 336.0, "En Tránsito")
        ]
        ph = "%s, %s, %s, %s, %s, %s, %s" if postgres_mode else "?, ?, ?, ?, ?, ?, ?"
        for co in compras:
            cur.execute(f"INSERT INTO compras (numero_oc, fecha, proveedor, insumo, cantidad, monto_total, estado) VALUES ({ph})", co)

    # Usuarios
    cur.execute("SELECT COUNT(*) AS c FROM usuarios;")
    row = cur.fetchone()
    count = row['c'] if isinstance(row, dict) else row[0]
    if count == 0:
        usuarios = [
            ("cramos", "Camila Ramos", "Recepcionista", "Agenda (CU01), Clientes (CU02), POS (CU03)"),
            ("aleida_admin", "Aleida Mendoza", "Gerente General", "Acceso Total (CU01-CU09), Aprobación de Anulaciones (CU04)"),
            ("csanchez", "Carmen Sánchez", "Terapeuta / Cosmiatra", "Consulta de Agenda propia, Historial de atenciones")
        ]
        ph = "%s, %s, %s, %s" if postgres_mode else "?, ?, ?, ?"
        for u in usuarios:
            cur.execute(f"INSERT INTO usuarios (usuario, nombre, rol, permisos) VALUES ({ph})", u)

    if not postgres_mode:
        conn.commit()
