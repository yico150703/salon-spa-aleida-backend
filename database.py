"""
=============================================================================
CAPA DE BASE DE DATOS - CONECTOR POSTGRESQL & SQLITE (RENDER & LOCAL)
Soporta despliegue nativo en Render PostgreSQL (DATABASE_URL)
Con fallback transparente a SQLite para desarrollo local sin dependencias externas.
SCHEMA OFICIAL CANÓNICO: 11 Tablas con nombres exactos de Clases de Rational Rose.
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
    """Garantiza la existencia de las 11 tablas con nombres idénticos a las clases de Rational Rose."""
    conn = get_connection()
    cur = get_cursor(conn)
    postgres_mode = is_postgres()

    try:
        cur.execute("DROP TABLE IF EXISTS anulaciones, compras, productos CASCADE;")
    except Exception:
        pass

    # 1. "Cliente"
    cur.execute("""
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
    """)

    # 2. "FichaEstetica"
    cur.execute("""
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
    """)

    # 3. "Cita"
    cur.execute("""
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
    """)

    # 4. "Servicio"
    cur.execute("""
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
    """)

    # 5. "Promocion"
    cur.execute("""
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
    """)

    # 6. "VentaComprobante"
    cur.execute("""
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
    """)

    # 7. "DetalleComprobante"
    item_pk = "SERIAL PRIMARY KEY" if postgres_mode else "INTEGER PRIMARY KEY AUTOINCREMENT"
    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS "DetalleComprobante" (
        item {item_pk},
        numerocomprobante VARCHAR(30) NOT NULL REFERENCES "VentaComprobante"(numerocomprobante) ON DELETE CASCADE,
        codigitem VARCHAR(30) NOT NULL,
        tipoitem VARCHAR(30) DEFAULT 'Servicio',
        descripcion TEXT NOT NULL,
        cantidad INTEGER NOT NULL DEFAULT 1,
        preciounitario NUMERIC(10,2) NOT NULL,
        subtotal NUMERIC(10,2) NOT NULL
    );
    """)

    # 8. "Pago"
    cur.execute("""
    CREATE TABLE IF NOT EXISTS "Pago" (
        codigpago VARCHAR(30) PRIMARY KEY,
        numerocomprobante VARCHAR(30) NOT NULL REFERENCES "VentaComprobante"(numerocomprobante) ON DELETE CASCADE,
        monto NUMERIC(10,2) NOT NULL,
        mediopago VARCHAR(40) NOT NULL,
        referenciaoperacion VARCHAR(60),
        fechahora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        estado VARCHAR(25) DEFAULT 'Aprobado'
    );
    """)

    # 9. "CajaSesion"
    cur.execute("""
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
    """)

    # 10. "MovimientoCaja"
    cur.execute("""
    CREATE TABLE IF NOT EXISTS "MovimientoCaja" (
        codigmovimiento VARCHAR(30) PRIMARY KEY,
        codigsesion VARCHAR(30) NOT NULL REFERENCES "CajaSesion"(codigsesion) ON DELETE CASCADE,
        tipomovimiento VARCHAR(30) NOT NULL,
        concepto TEXT NOT NULL,
        monto NUMERIC(10,2) NOT NULL,
        fechahora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        autorizadopor VARCHAR(100) DEFAULT 'Administrador'
    );
    """)

    # 11. "Usuario"
    cur.execute("""
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
    """)

    # Vista sinónima "VentasComprobante"
    try:
        if postgres_mode:
            cur.execute('CREATE OR REPLACE VIEW "VentasComprobante" AS SELECT * FROM "VentaComprobante";')
        else:
            cur.execute('CREATE VIEW IF NOT EXISTS "VentasComprobante" AS SELECT * FROM "VentaComprobante";')
    except Exception:
        pass

    if not postgres_mode:
        conn.commit()
    conn.close()
    logger.info("Base de datos verificada con las 11 tablas canónicas de Rational Rose (CamelCase).")
