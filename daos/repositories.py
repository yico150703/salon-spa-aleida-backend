"""
=============================================================================
CAPA 3: ACCESO A DATOS (PATRÓN DAO / REPOSITORIOS)
Persistencia transaccional sobre PostgreSQL (en Render) o SQLite (en Local)
Conforme a la Sección 3.8.2 del Documento de Arquitectura
=============================================================================
"""

from typing import List, Optional
from datetime import datetime
import logging
from models.entities import Cliente, Cita, Servicio, Producto, Venta, Caja, Compra, Proveedor, Usuario
from database import get_connection, get_cursor, is_postgres

logger = logging.getLogger("spa_daos")

class BaseDAO:
    def _ph(self, count: int) -> str:
        """Devuelve placeholders acordes al motor: %s para PostgreSQL, ? para SQLite."""
        return ", ".join(["%s" if is_postgres() else "?"] * count)

class ClienteDAO(BaseDAO):
    def find_all(self) -> List[Cliente]:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            cur.execute("SELECT dni, nombre, telefono, preferencias, visitas, ultima_visita FROM clientes ORDER BY nombre ASC;")
            rows = cur.fetchall()
            conn.close()
            return [
                Cliente(
                    dni=r["dni"],
                    nombre=r["nombre"],
                    telefono=r["telefono"] or "",
                    preferencias=r["preferencias"] or "",
                    visitas=int(r["visitas"] or 1),
                    ultima_visita=r["ultima_visita"] or ""
                )
                for r in rows
            ]
        except Exception as e:
            logger.error("Error en ClienteDAO.find_all: %s", e)
            return []

    def find_by_dni(self, dni: str) -> Optional[Cliente]:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            ph = "%s" if is_postgres() else "?"
            cur.execute(f"SELECT dni, nombre, telefono, preferencias, visitas, ultima_visita FROM clientes WHERE dni = {ph};", (dni,))
            r = cur.fetchone()
            conn.close()
            if r:
                return Cliente(
                    dni=r["dni"],
                    nombre=r["nombre"],
                    telefono=r["telefono"] or "",
                    preferencias=r["preferencias"] or "",
                    visitas=int(r["visitas"] or 1),
                    ultima_visita=r["ultima_visita"] or ""
                )
            return None
        except Exception as e:
            logger.error("Error en ClienteDAO.find_by_dni: %s", e)
            return None

    def save(self, cliente: Cliente) -> Cliente:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            existing = self.find_by_dni(cliente.dni)
            today = datetime.now().strftime("%Y-%m-%d")
            
            if existing:
                ph = "%s" if is_postgres() else "?"
                cur.execute(
                    f"UPDATE clientes SET nombre = {ph}, telefono = {ph}, preferencias = {ph}, visitas = visitas + 1, ultima_visita = {ph} WHERE dni = {ph};",
                    (cliente.nombre, cliente.telefono, cliente.preferencias, today, cliente.dni)
                )
                cliente.visitas = existing.visitas + 1
                cliente.ultima_visita = today
            else:
                ph = self._ph(6)
                cur.execute(
                    f"INSERT INTO clientes (dni, nombre, telefono, preferencias, visitas, ultima_visita) VALUES ({ph});",
                    (cliente.dni, cliente.nombre, cliente.telefono, cliente.preferencias, cliente.visitas, today)
                )
            if not is_postgres():
                conn.commit()
            conn.close()
            return cliente
        except Exception as e:
            logger.error("Error en ClienteDAO.save: %s", e)
            return cliente


class CitaDAO(BaseDAO):
    def find_all(self) -> List[Cita]:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            cur.execute("SELECT id, hora, fecha, cliente, dni, servicio, especialista, estado, monto, cobrado, motivo_cancelacion FROM citas ORDER BY id ASC;")
            rows = cur.fetchall()
            conn.close()
            return [
                Cita(
                    id=r["id"],
                    hora=r["hora"],
                    fecha=r["fecha"],
                    cliente=r["cliente"],
                    dni=r["dni"],
                    servicio=r["servicio"],
                    especialista=r["especialista"],
                    estado=r["estado"],
                    monto=float(r["monto"] or 0.0),
                    cobrado=bool(r["cobrado"]),
                    motivo_cancelacion=r["motivo_cancelacion"]
                )
                for r in rows
            ]
        except Exception as e:
            logger.error("Error en CitaDAO.find_all: %s", e)
            return []

    def find_by_id(self, cita_id: int) -> Optional[Cita]:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            ph = "%s" if is_postgres() else "?"
            cur.execute(f"SELECT id, hora, fecha, cliente, dni, servicio, especialista, estado, monto, cobrado, motivo_cancelacion FROM citas WHERE id = {ph};", (cita_id,))
            r = cur.fetchone()
            conn.close()
            if r:
                return Cita(
                    id=r["id"],
                    hora=r["hora"],
                    fecha=r["fecha"],
                    cliente=r["cliente"],
                    dni=r["dni"],
                    servicio=r["servicio"],
                    especialista=r["especialista"],
                    estado=r["estado"],
                    monto=float(r["monto"] or 0.0),
                    cobrado=bool(r["cobrado"]),
                    motivo_cancelacion=r["motivo_cancelacion"]
                )
            return None
        except Exception as e:
            logger.error("Error en CitaDAO.find_by_id: %s", e)
            return None

    def find_conflict(self, fecha: str, hora: str, especialista: str) -> Optional[Cita]:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            ph = "%s" if is_postgres() else "?"
            cur.execute(
                f"SELECT id, hora, fecha, cliente, dni, servicio, especialista, estado, monto, cobrado, motivo_cancelacion "
                f"FROM citas WHERE fecha = {ph} AND hora = {ph} AND especialista = {ph} AND estado NOT IN ('Cancelada', 'No Asistió');",
                (fecha, hora, especialista)
            )
            r = cur.fetchone()
            conn.close()
            if r:
                return Cita(
                    id=r["id"],
                    hora=r["hora"],
                    fecha=r["fecha"],
                    cliente=r["cliente"],
                    dni=r["dni"],
                    servicio=r["servicio"],
                    especialista=r["especialista"],
                    estado=r["estado"],
                    monto=float(r["monto"] or 0.0),
                    cobrado=bool(r["cobrado"]),
                    motivo_cancelacion=r["motivo_cancelacion"]
                )
            return None
        except Exception as e:
            logger.error("Error en CitaDAO.find_conflict: %s", e)
            return None

    def save(self, cita: Cita) -> Cita:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            if is_postgres():
                cur.execute(
                    "INSERT INTO citas (hora, fecha, cliente, dni, servicio, especialista, estado, monto, cobrado, motivo_cancelacion) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;",
                    (cita.hora, cita.fecha, cita.cliente, cita.dni, cita.servicio, cita.especialista, cita.estado, cita.monto, cita.cobrado, cita.motivo_cancelacion)
                )
                cita.id = cur.fetchone()["id"]
            else:
                cur.execute(
                    "INSERT INTO citas (hora, fecha, cliente, dni, servicio, especialista, estado, monto, cobrado, motivo_cancelacion) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                    (cita.hora, cita.fecha, cita.cliente, cita.dni, cita.servicio, cita.especialista, cita.estado, cita.monto, cita.cobrado, cita.motivo_cancelacion)
                )
                conn.commit()
                cita.id = cur.lastrowid
            conn.close()
            return cita
        except Exception as e:
            logger.error("Error en CitaDAO.save: %s", e)
            return cita

    def update(self, cita: Cita) -> Cita:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            ph = "%s" if is_postgres() else "?"
            cur.execute(
                f"UPDATE citas SET hora = {ph}, fecha = {ph}, cliente = {ph}, dni = {ph}, servicio = {ph}, "
                f"especialista = {ph}, estado = {ph}, monto = {ph}, cobrado = {ph}, motivo_cancelacion = {ph} WHERE id = {ph};",
                (cita.hora, cita.fecha, cita.cliente, cita.dni, cita.servicio, cita.especialista, cita.estado, cita.monto, cita.cobrado, cita.motivo_cancelacion, cita.id)
            )
            if not is_postgres():
                conn.commit()
            conn.close()
            return cita
        except Exception as e:
            logger.error("Error en CitaDAO.update: %s", e)
            return cita


class VentaDAO(BaseDAO):
    def find_all(self) -> List[Venta]:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            cur.execute("SELECT id, numero_boleta, fecha, cliente, servicio, subtotal, igv, descuento, total, medio_pago, estado, nota_credito FROM ventas ORDER BY id DESC;")
            rows = cur.fetchall()
            conn.close()
            return [
                Venta(
                    id=r["id"],
                    numero_boleta=r["numero_boleta"],
                    fecha=r["fecha"],
                    cliente=r["cliente"],
                    servicio=r["servicio"],
                    subtotal=float(r["subtotal"] or 0.0),
                    igv=float(r["igv"] or 0.0),
                    descuento=float(r["descuento"] or 0.0),
                    total=float(r["total"] or 0.0),
                    medio_pago=r["medio_pago"],
                    estado=r["estado"],
                    nota_credito=r["nota_credito"]
                )
                for r in rows
            ]
        except Exception as e:
            logger.error("Error en VentaDAO.find_all: %s", e)
            return []

    def find_by_ticket(self, numero_boleta: str) -> Optional[Venta]:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            ph = "%s" if is_postgres() else "?"
            cur.execute(f"SELECT id, numero_boleta, fecha, cliente, servicio, subtotal, igv, descuento, total, medio_pago, estado, nota_credito FROM ventas WHERE numero_boleta = {ph};", (numero_boleta,))
            r = cur.fetchone()
            conn.close()
            if r:
                return Venta(
                    id=r["id"],
                    numero_boleta=r["numero_boleta"],
                    fecha=r["fecha"],
                    cliente=r["cliente"],
                    servicio=r["servicio"],
                    subtotal=float(r["subtotal"] or 0.0),
                    igv=float(r["igv"] or 0.0),
                    descuento=float(r["descuento"] or 0.0),
                    total=float(r["total"] or 0.0),
                    medio_pago=r["medio_pago"],
                    estado=r["estado"],
                    nota_credito=r["nota_credito"]
                )
            return None
        except Exception as e:
            logger.error("Error en VentaDAO.find_by_ticket: %s", e)
            return None

    def save(self, venta: Venta) -> Venta:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            if is_postgres():
                cur.execute(
                    "INSERT INTO ventas (numero_boleta, fecha, cliente, servicio, subtotal, igv, descuento, total, medio_pago, estado, nota_credito) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;",
                    (venta.numero_boleta, venta.fecha, venta.cliente, venta.servicio, venta.subtotal, venta.igv, venta.descuento, venta.total, venta.medio_pago, venta.estado, venta.nota_credito)
                )
                venta.id = cur.fetchone()["id"]
            else:
                cur.execute(
                    "INSERT INTO ventas (numero_boleta, fecha, cliente, servicio, subtotal, igv, descuento, total, medio_pago, estado, nota_credito) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                    (venta.numero_boleta, venta.fecha, venta.cliente, venta.servicio, venta.subtotal, venta.igv, venta.descuento, venta.total, venta.medio_pago, venta.estado, venta.nota_credito)
                )
                conn.commit()
                venta.id = cur.lastrowid
            conn.close()
            return venta
        except Exception as e:
            logger.error("Error en VentaDAO.save: %s", e)
            return venta

    def save_anulacion(self, anulacion_data: dict) -> dict:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            if is_postgres():
                cur.execute(
                    "INSERT INTO anulaciones (fecha, boleta, nota_credito, monto, motivo, autorizado_por) "
                    "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;",
                    (anulacion_data["fecha"], anulacion_data["boleta"], anulacion_data["nota_credito"], anulacion_data["monto"], anulacion_data["motivo"], anulacion_data["autorizado_por"])
                )
                anulacion_data["id"] = cur.fetchone()["id"]
            else:
                cur.execute(
                    "INSERT INTO anulaciones (fecha, boleta, nota_credito, monto, motivo, autorizado_por) "
                    "VALUES (?, ?, ?, ?, ?, ?);",
                    (anulacion_data["fecha"], anulacion_data["boleta"], anulacion_data["nota_credito"], anulacion_data["monto"], anulacion_data["motivo"], anulacion_data["autorizado_por"])
                )
                conn.commit()
                anulacion_data["id"] = cur.lastrowid
            conn.close()
            return anulacion_data
        except Exception as e:
            logger.error("Error en VentaDAO.save_anulacion: %s", e)
            return anulacion_data

    def get_anulaciones(self) -> List[dict]:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            cur.execute("SELECT id, fecha, boleta, nota_credito, monto, motivo, autorizado_por FROM anulaciones ORDER BY id DESC;")
            rows = cur.fetchall()
            conn.close()
            return [
                {
                    "id": r["id"],
                    "fecha": r["fecha"],
                    "boleta": r["boleta"],
                    "nota_credito": r["nota_credito"],
                    "monto": float(r["monto"]),
                    "motivo": r["motivo"],
                    "autorizado_por": r["autorizado_por"]
                }
                for r in rows
            ]
        except Exception as e:
            logger.error("Error en VentaDAO.get_anulaciones: %s", e)
            return []


class CajaDAO(BaseDAO):
    def get_caja_actual(self) -> Caja:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            cur.execute("SELECT id, fecha, apertura, efectivo, digital, egresos, saldo_teorico, arqueo_fisico, diferencia, estado, turno FROM caja ORDER BY id DESC LIMIT 1;")
            r = cur.fetchone()
            conn.close()
            if r:
                caja = Caja(
                    id=r["id"],
                    fecha=r["fecha"],
                    apertura=float(r["apertura"] or 0.0),
                    efectivo=float(r["efectivo"] or 0.0),
                    digital=float(r["digital"] or 0.0),
                    egresos=float(r["egresos"] or 0.0),
                    saldo_teorico=float(r["saldo_teorico"] or 0.0),
                    arqueo_fisico=float(r["arqueo_fisico"]) if r["arqueo_fisico"] is not None else None,
                    diferencia=float(r["diferencia"]) if r["diferencia"] is not None else None,
                    estado=r["estado"],
                    turno=r["turno"]
                )
                caja.saldo_teorico = caja.apertura + caja.efectivo + caja.digital - caja.egresos
                return caja
        except Exception as e:
            logger.error("Error en CajaDAO.get_caja_actual: %s", e)
        return Caja(1, datetime.now().strftime("%Y-%m-%d"), 150.0, 720.0, 1580.0, 45.0, 2405.0)

    def get_movimientos(self) -> List[dict]:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            cur.execute("SELECT id, hora, tipo, monto, detalle FROM caja_movimientos ORDER BY id ASC;")
            rows = cur.fetchall()
            conn.close()
            return [
                {
                    "hora": r["hora"],
                    "tipo": r["tipo"],
                    "monto": float(r["monto"]),
                    "detalle": r["detalle"]
                }
                for r in rows
            ]
        except Exception as e:
            logger.error("Error en CajaDAO.get_movimientos: %s", e)
            return []

    def add_movimiento(self, tipo: str, monto: float, detalle: str):
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            hora = datetime.now().strftime("%I:%M %p")
            ph = "%s, %s, %s, %s" if is_postgres() else "?, ?, ?, ?"
            cur.execute(f"INSERT INTO caja_movimientos (hora, tipo, monto, detalle) VALUES ({ph});", (hora, tipo, monto, detalle))
            if not is_postgres():
                conn.commit()
            conn.close()
        except Exception as e:
            logger.error("Error en CajaDAO.add_movimiento: %s", e)

    def update_caja(self, caja: Caja) -> Caja:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            ph = "%s" if is_postgres() else "?"
            cur.execute(
                f"UPDATE caja SET apertura = {ph}, efectivo = {ph}, digital = {ph}, egresos = {ph}, "
                f"saldo_teorico = {ph}, arqueo_fisico = {ph}, diferencia = {ph}, estado = {ph}, turno = {ph} WHERE id = {ph};",
                (caja.apertura, caja.efectivo, caja.digital, caja.egresos, caja.saldo_teorico, caja.arqueo_fisico, caja.diferencia, caja.estado, caja.turno, caja.id)
            )
            if not is_postgres():
                conn.commit()
            conn.close()
            return caja
        except Exception as e:
            logger.error("Error en CajaDAO.update_caja: %s", e)
            return caja


class ProductoDAO(BaseDAO):
    def find_all(self) -> List[Producto]:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            cur.execute("SELECT id, nombre, proveedor, stock, stock_min, costo, precio_venta, alerta FROM productos ORDER BY id ASC;")
            rows = cur.fetchall()
            conn.close()
            return [
                Producto(
                    id=r["id"],
                    nombre=r["nombre"],
                    proveedor=r["proveedor"],
                    stock=r["stock"],
                    stock_min=r["stock_min"],
                    costo=float(r["costo"]),
                    precio_venta=float(r["precio_venta"]),
                    alerta=bool(r["alerta"])
                )
                for r in rows
            ]
        except Exception as e:
            logger.error("Error en ProductoDAO.find_all: %s", e)
            return []

    def save(self, prod: Producto) -> Producto:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            if is_postgres():
                cur.execute(
                    "INSERT INTO productos (nombre, proveedor, stock, stock_min, costo, precio_venta, alerta) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;",
                    (prod.nombre, prod.proveedor, prod.stock, prod.stock_min, prod.costo, prod.precio_venta, prod.alerta)
                )
                prod.id = cur.fetchone()["id"]
            else:
                cur.execute(
                    "INSERT INTO productos (nombre, proveedor, stock, stock_min, costo, precio_venta, alerta) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?);",
                    (prod.nombre, prod.proveedor, prod.stock, prod.stock_min, prod.costo, prod.precio_venta, prod.alerta)
                )
                conn.commit()
                prod.id = cur.lastrowid
            conn.close()
            return prod
        except Exception as e:
            logger.error("Error en ProductoDAO.save: %s", e)
            return prod

    def update_stock(self, prod_id: int, delta: int) -> Optional[Producto]:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            ph = "%s" if is_postgres() else "?"
            cur.execute(f"UPDATE productos SET stock = stock + {ph} WHERE id = {ph};", (delta, prod_id))
            cur.execute(f"UPDATE productos SET alerta = (stock <= stock_min) WHERE id = {ph};", (prod_id,))
            if not is_postgres():
                conn.commit()
            cur.execute(f"SELECT id, nombre, proveedor, stock, stock_min, costo, precio_venta, alerta FROM productos WHERE id = {ph};", (prod_id,))
            r = cur.fetchone()
            conn.close()
            if r:
                return Producto(
                    id=r["id"],
                    nombre=r["nombre"],
                    proveedor=r["proveedor"],
                    stock=r["stock"],
                    stock_min=r["stock_min"],
                    costo=float(r["costo"]),
                    precio_venta=float(r["precio_venta"]),
                    alerta=bool(r["alerta"])
                )
        except Exception as e:
            logger.error("Error en ProductoDAO.update_stock: %s", e)
        return None


class CompraDAO(BaseDAO):
    def find_all(self) -> List[Compra]:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            cur.execute("SELECT id, numero_oc, fecha, proveedor, insumo, cantidad, monto_total, estado FROM compras ORDER BY id DESC;")
            rows = cur.fetchall()
            conn.close()
            return [
                Compra(
                    id=r["id"],
                    numero_oc=r["numero_oc"],
                    fecha=r["fecha"],
                    proveedor=r["proveedor"],
                    insumo=r["insumo"],
                    cantidad=r["cantidad"],
                    monto_total=float(r["monto_total"]),
                    estado=r["estado"]
                )
                for r in rows
            ]
        except Exception as e:
            logger.error("Error en CompraDAO.find_all: %s", e)
            return []

    def save(self, compra: Compra) -> Compra:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            if is_postgres():
                cur.execute(
                    "INSERT INTO compras (numero_oc, fecha, proveedor, insumo, cantidad, monto_total, estado) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;",
                    (compra.numero_oc, compra.fecha, compra.proveedor, compra.insumo, compra.cantidad, compra.monto_total, compra.estado)
                )
                compra.id = cur.fetchone()["id"]
            else:
                cur.execute(
                    "INSERT INTO compras (numero_oc, fecha, proveedor, insumo, cantidad, monto_total, estado) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?);",
                    (compra.numero_oc, compra.fecha, compra.proveedor, compra.insumo, compra.cantidad, compra.monto_total, compra.estado)
                )
                conn.commit()
                compra.id = cur.lastrowid
            conn.close()
            return compra
        except Exception as e:
            logger.error("Error en CompraDAO.save: %s", e)
            return compra


class ServicioDAO(BaseDAO):
    def find_all(self) -> List[Servicio]:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            cur.execute("SELECT id, nombre, categoria, duracion, precio, comision, activo FROM servicios WHERE activo = TRUE ORDER BY id ASC;")
            rows = cur.fetchall()
            conn.close()
            return [
                Servicio(
                    id=r["id"],
                    nombre=r["nombre"],
                    categoria=r["categoria"],
                    duracion=r["duracion"],
                    precio=float(r["precio"]),
                    comision=r["comision"],
                    activo=bool(r["activo"])
                )
                for r in rows
            ]
        except Exception as e:
            logger.error("Error en ServicioDAO.find_all: %s", e)
            return []

    def save(self, serv: Servicio) -> Servicio:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            if is_postgres():
                cur.execute(
                    "INSERT INTO servicios (nombre, categoria, duracion, precio, comision, activo) "
                    "VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;",
                    (serv.nombre, serv.categoria, serv.duracion, serv.precio, serv.comision, serv.activo)
                )
                serv.id = cur.fetchone()["id"]
            else:
                cur.execute(
                    "INSERT INTO servicios (nombre, categoria, duracion, precio, comision, activo) "
                    "VALUES (?, ?, ?, ?, ?, ?);",
                    (serv.nombre, serv.categoria, serv.duracion, serv.precio, serv.comision, serv.activo)
                )
                conn.commit()
                serv.id = cur.lastrowid
            conn.close()
            return serv
        except Exception as e:
            logger.error("Error en ServicioDAO.save: %s", e)
            return serv


class UsuarioDAO(BaseDAO):
    def find_all(self) -> List[Usuario]:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            cur.execute("SELECT usuario, nombre, rol, permisos, activo FROM usuarios WHERE activo = TRUE ORDER BY usuario ASC;")
            rows = cur.fetchall()
            conn.close()
            return [
                Usuario(
                    usuario=r["usuario"],
                    nombre=r["nombre"],
                    rol=r["rol"],
                    permisos=r["permisos"],
                    activo=bool(r["activo"])
                )
                for r in rows
            ]
        except Exception as e:
            logger.error("Error en UsuarioDAO.find_all: %s", e)
            return []

    def save(self, user: Usuario) -> Usuario:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            ph = self._ph(4)
            cur.execute(
                f"INSERT INTO usuarios (usuario, nombre, rol, permisos) VALUES ({ph});",
                (user.usuario, user.nombre, user.rol, user.permisos)
            )
            if not is_postgres():
                conn.commit()
            conn.close()
            return user
        except Exception as e:
            logger.error("Error en UsuarioDAO.save: %s", e)
            return user
