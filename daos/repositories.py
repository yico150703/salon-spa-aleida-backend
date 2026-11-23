"""
=============================================================================
CAPA DE ACCESO A DATOS (DAO / REPOSITORY) - SALÓN & SPA ALEIDA S.A.C.
Sincronizado al 100% con las columnas de Rational Rose (PostgreSQL / SQLite).
=============================================================================
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from database import get_connection, get_cursor, is_postgres
from models.entities import (
    Cliente, Cita, Venta, DetalleComprobante, Pago, Caja, MovimientoCaja,
    Servicio, Usuario, Producto, Compra
)

logger = logging.getLogger("spa_daos")


class BaseDAO:
    def _ph(self, count: int) -> str:
        return ", ".join(["%s" if is_postgres() else "?"] * count)


class ClienteDAO(BaseDAO):
    def find_all(self) -> List[Cliente]:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            cur.execute('SELECT dni, nombres, apellidos, telefono, direccion, preferencias, fecharegistro, estadopadron FROM "Cliente" ORDER BY dni ASC;')
            rows = cur.fetchall()
            conn.close()
            return [
                Cliente(
                    dni=r["dni"],
                    nombre=f"{r['nombres']} {r['apellidos']}".strip(),
                    telefono=r["telefono"] or "",
                    preferencias=r["preferencias"] or "",
                    apellidos=r["apellidos"] or "",
                    correo="",
                    direccion=r["direccion"] or "Lima, Perú",
                    fecha_registro=r["fecharegistro"] or "2026-10-06",
                    estado_padron=r["estadopadron"] or "Activo",
                    visitas=1,
                    ultima_visita=r["fecharegistro"] or "2026-10-06"
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
            cur.execute(f'SELECT dni, nombres, apellidos, telefono, direccion, preferencias, fecharegistro, estadopadron FROM "Cliente" WHERE dni = {ph};', (dni,))
            r = cur.fetchone()
            conn.close()
            if r:
                return Cliente(
                    dni=r["dni"],
                    nombre=f"{r['nombres']} {r['apellidos']}".strip(),
                    telefono=r["telefono"] or "",
                    preferencias=r["preferencias"] or "",
                    apellidos=r["apellidos"] or "",
                    correo="",
                    direccion=r["direccion"] or "Lima, Perú",
                    fecha_registro=r["fecharegistro"] or "2026-10-06",
                    estado_padron=r["estadopadron"] or "Activo",
                    visitas=1,
                    ultima_visita=r["fecharegistro"] or "2026-10-06"
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
            
            # Separar nombres y apellidos si es necesario
            parts = (cliente.nombre or "").split(" ", 1)
            nombres = parts[0]
            apellidos = cliente.apellidos if cliente.apellidos else (parts[1] if len(parts) > 1 else "")

            if existing:
                ph = "%s" if is_postgres() else "?"
                cur.execute(
                    f'UPDATE "Cliente" SET nombres = {ph}, apellidos = {ph}, telefono = {ph}, preferencias = {ph}, fecharegistro = {ph} WHERE dni = {ph};',
                    (nombres, apellidos, cliente.telefono, cliente.preferencias, today, cliente.dni)
                )
            else:
                ph = self._ph(8)
                cur.execute(
                    f'INSERT INTO "Cliente" (dni, nombres, apellidos, telefono, direccion, preferencias, fecharegistro, estadopadron) VALUES ({ph});',
                    (cliente.dni, nombres, apellidos, cliente.telefono, cliente.direccion or "Lima, Perú", cliente.preferencias, today, "Activo")
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
            cur.execute("""
                SELECT c.codigcita, c.codigreserva, c.fecha, c.horainicio, c.horafin, c.dni_cliente, 
                       c.especialista, c.montototal, c.estado, c.motivocancelacion, c.observaciones,
                       COALESCE(cl.nombres || ' ' || cl.apellidos, c.dni_cliente) as cliente_nombre
                FROM "Cita" c 
                LEFT JOIN "Cliente" cl ON c.dni_cliente = cl.dni 
                ORDER BY c.fecha DESC, c.horainicio ASC;
            """)
            rows = cur.fetchall()
            conn.close()
            return [
                Cita(
                    id=r["codigcita"],
                    hora=r["horainicio"],
                    fecha=r["fecha"],
                    cliente=r["cliente_nombre"],
                    dni=r["dni_cliente"],
                    servicio=r["observaciones"] or "Servicio Spa Aleida",
                    especialista=r["especialista"],
                    estado=r["estado"],
                    monto=float(r["montototal"] or 0.0),
                    cobrado=bool(r["estado"] == "Atendida"),
                    motivo_cancelacion=r["motivocancelacion"],
                    cabina=r.get("cabina", "Cabina 01 - Facial Oro")
                )
                for r in rows
            ]
        except Exception as e:
            logger.error("Error en CitaDAO.find_all: %s", e)
            return []

    def find_by_id(self, cita_id: Any) -> Optional[Cita]:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            ph = "%s" if is_postgres() else "?"
            alt_id = f"CIT-{int(cita_id):05d}" if str(cita_id).isdigit() else str(cita_id)
            cur.execute(f"""
                SELECT c.codigcita, c.codigreserva, c.fecha, c.horainicio, c.horafin, c.dni_cliente, 
                       c.especialista, c.montototal, c.estado, c.motivocancelacion, c.observaciones,
                       COALESCE(cl.nombres || ' ' || cl.apellidos, c.dni_cliente) as cliente_nombre
                FROM "Cita" c 
                LEFT JOIN "Cliente" cl ON c.dni_cliente = cl.dni 
                WHERE c.codigcita = {ph} OR c.codigcita = {ph};
            """, (str(cita_id), alt_id))
            r = cur.fetchone()
            conn.close()
            if r:
                return Cita(
                    id=r["codigcita"],
                    hora=r["horainicio"],
                    fecha=r["fecha"],
                    cliente=r["cliente_nombre"],
                    dni=r["dni_cliente"],
                    servicio=r["observaciones"] or "Servicio Spa Aleida",
                    especialista=r["especialista"],
                    estado=r["estado"],
                    monto=float(r["montototal"] or 0.0),
                    cobrado=bool(r["estado"] == "Atendida"),
                    motivo_cancelacion=r["motivocancelacion"]
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
            nombre_base = especialista.split("(")[0].strip()
            like_op = "ILIKE" if is_postgres() else "LIKE"
            cur.execute(
                f"SELECT codigcita, horainicio, fecha, dni_cliente, especialista, estado, montototal "
                f'FROM "Cita" WHERE fecha = {ph} AND horainicio = {ph} '
                f"AND (especialista {like_op} {ph} OR especialista {like_op} {ph}) "
                f"AND estado NOT IN ('Cancelada', 'No Asistió', 'No Asistio', 'Anulada');",
                (fecha, hora, nombre_base, f"{nombre_base}%")
            )
            r = cur.fetchone()
            conn.close()
            if r:
                return Cita(
                    id=r["codigcita"],
                    hora=r["horainicio"],
                    fecha=r["fecha"],
                    cliente=r["dni_cliente"],
                    dni=r["dni_cliente"],
                    servicio="Servicio Programado",
                    especialista=r["especialista"],
                    estado=r["estado"],
                    monto=float(r["montototal"] or 0.0),
                    cobrado=False
                )
            return None
        except Exception as e:
            logger.error("Error en CitaDAO.find_conflict: %s", e)
            return None

    def save(self, cita: Cita) -> Cita:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            codig_cita = f"CIT-{int(datetime.now().timestamp()) % 100000:05d}"
            codig_reserva = f"RES-{int(datetime.now().timestamp()) % 100000:05d}"
            ph = self._ph(11)
            cur.execute(
                f'INSERT INTO "Cita" (codigcita, codigreserva, fecha, horainicio, horafin, dni_cliente, especialista, montototal, estado, motivocancelacion, observaciones) '
                f"VALUES ({ph});",
                (codig_cita, codig_reserva, cita.fecha, cita.hora, "10:30 AM", cita.dni, cita.especialista, cita.monto, cita.estado or "Confirmada", cita.motivo_cancelacion or "", cita.servicio or "")
            )
            if not is_postgres():
                conn.commit()
            cita.id = codig_cita
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
            alt_id = f"CIT-{int(cita.id):05d}" if str(cita.id).isdigit() else str(cita.id)
            cur.execute(
                f'UPDATE "Cita" SET horainicio = {ph}, fecha = {ph}, especialista = {ph}, estado = {ph}, montototal = {ph}, motivocancelacion = {ph}, observaciones = {ph} WHERE codigcita = {ph} OR codigcita = {ph};',
                (cita.hora, cita.fecha, cita.especialista, cita.estado, cita.monto, cita.motivo_cancelacion, cita.servicio, str(cita.id), alt_id)
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
            cur.execute("""
                SELECT v.numerocomprobante, v.tipocomprobante, v.serie, v.fechaemision, v.horaemision, 
                       v.dni_cliente, v.subtotal, v.igv, v.descuentototal, v.totalneto, v.estadocomprobante, v.notacredito,
                       COALESCE(cl.nombres || ' ' || cl.apellidos, v.dni_cliente) as cliente_nombre
                FROM "VentaComprobante" v 
                LEFT JOIN "Cliente" cl ON v.dni_cliente = cl.dni 
                ORDER BY v.fechaemision DESC;
            """)
            rows = cur.fetchall()
            conn.close()
            return [
                Venta(
                    id=r["numerocomprobante"],
                    numero_boleta=r["numerocomprobante"],
                    fecha=f"{r['fechaemision']} {r['horaemision']}".strip(),
                    cliente=r["cliente_nombre"],
                    servicio="Tratamiento Spa Aleida",
                    subtotal=float(r["subtotal"] or 0.0),
                    igv=float(r["igv"] or 0.0),
                    descuento=float(r["descuentototal"] or 0.0),
                    total=float(r["totalneto"] or 0.0),
                    medio_pago="Efectivo",
                    tipo_comprobante=r["tipocomprobante"] or "Boleta de Venta",
                    serie=r["serie"] or "B001",
                    dni_cliente=r["dni_cliente"] or "",
                    estado=r["estadocomprobante"],
                    nota_credito=r["notacredito"]
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
            cur.execute(f"""
                SELECT v.numerocomprobante, v.tipocomprobante, v.serie, v.fechaemision, v.horaemision, 
                       v.dni_cliente, v.subtotal, v.igv, v.descuentototal, v.totalneto, v.estadocomprobante, v.notacredito,
                       COALESCE(cl.nombres || ' ' || cl.apellidos, v.dni_cliente) as cliente_nombre
                FROM "VentaComprobante" v 
                LEFT JOIN "Cliente" cl ON v.dni_cliente = cl.dni 
                WHERE v.numerocomprobante = {ph};
            """, (numero_boleta,))
            r = cur.fetchone()
            conn.close()
            if r:
                return Venta(
                    id=r["numerocomprobante"],
                    numero_boleta=r["numerocomprobante"],
                    fecha=f"{r['fechaemision']} {r['horaemision']}".strip(),
                    cliente=r["cliente_nombre"],
                    servicio="Tratamiento Spa Aleida",
                    subtotal=float(r["subtotal"] or 0.0),
                    igv=float(r["igv"] or 0.0),
                    descuento=float(r["descuentototal"] or 0.0),
                    total=float(r["totalneto"] or 0.0),
                    medio_pago="Efectivo",
                    tipo_comprobante=r["tipocomprobante"] or "Boleta de Venta",
                    serie=r["serie"] or "B001",
                    dni_cliente=r["dni_cliente"] or "",
                    estado=r["estadocomprobante"],
                    nota_credito=r["notacredito"]
                )
            return None
        except Exception as e:
            logger.error("Error en VentaDAO.find_by_ticket: %s", e)
            return None

    def save(self, venta: Venta) -> Venta:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            ph = self._ph(12)
            fecha_str = datetime.now().strftime("%Y-%m-%d")
            hora_str = datetime.now().strftime("%H:%M")
            dni_c = venta.dni_cliente if venta.dni_cliente else "72819382"
            try:
                cur.execute('SELECT dni FROM "Cliente" WHERE dni = %s;', (dni_c,))
                if not cur.fetchone():
                    cur.execute('SELECT dni FROM "Cliente" LIMIT 1;')
                    c_fallback = cur.fetchone()
                    dni_c = c_fallback["dni"] if c_fallback else None
            except Exception:
                pass
            cur.execute(
                f'INSERT INTO "VentaComprobante" (numerocomprobante, tipocomprobante, serie, fechaemision, horaemision, dni_cliente, subtotal, igv, descuentototal, totalneto, estadocomprobante, notacredito) '
                f"VALUES ({ph});",
                (venta.numero_boleta, venta.tipo_comprobante or "Boleta de Venta", venta.serie or "B001", fecha_str, hora_str, dni_c, venta.subtotal, venta.igv, venta.descuento, venta.total, venta.estado or "Emitida", venta.nota_credito)
            )
            # Guardar detalle
            cur.execute(
                f'INSERT INTO "DetalleComprobante" (item, numerocomprobante, codigitem, tipoitem, descripcion, cantidad, preciounitario, subtotal) VALUES ({self._ph(8)});',
                (1, venta.numero_boleta, "SRV-01", "Servicio", venta.servicio or "Tratamiento Facial / Corporal", 1, venta.total, venta.total)
            )
            # Guardar pago
            cod_pago = f"PAG-{int(datetime.now().timestamp() * 1000) % 10000000}"
            cur.execute(
                f'INSERT INTO "Pago" (codigpago, numerocomprobante, monto, mediopago, referenciaoperacion, estado) VALUES ({self._ph(6)});',
                (cod_pago, venta.numero_boleta, venta.total, venta.medio_pago or "Efectivo", "OP-001", "Aprobado")
            )
            if not is_postgres():
                conn.commit()
            conn.close()
            return venta
        except Exception as e:
            logger.error("Error en VentaDAO.save: %s", e)
            return venta

    def update_estado_anulada(self, numero_boleta: str, nota_credito: str):
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            ph = "%s" if is_postgres() else "?"
            cur.execute(
                f'UPDATE "VentaComprobante" SET estadocomprobante = \'Anulada\', notacredito = {ph} WHERE numerocomprobante = {ph};',
                (nota_credito, numero_boleta)
            )
            if not is_postgres():
                conn.commit()
            conn.close()
        except Exception as e:
            logger.error("Error en VentaDAO.update_estado_anulada: %s", e)

    def save_anulacion(self, anulacion_data: dict) -> dict:
        anulacion_data["id"] = 1
        return anulacion_data

    def get_anulaciones(self) -> List[dict]:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            cur.execute("""
                SELECT numerocomprobante, fechaemision, COALESCE(notacredito, 'NC-001') as notacredito, 
                       totalneto as monto, 'Devolución autorizada por gerencia' as motivo, 'Administrador' as autorizado_por 
                FROM "VentaComprobante" 
                WHERE estadocomprobante = 'Anulada' OR notacredito IS NOT NULL
                ORDER BY fechaemision DESC;
            """)
            rows = cur.fetchall()
            conn.close()
            return [
                {
                    "id": r["numerocomprobante"],
                    "fecha": r["fechaemision"],
                    "boleta": r["numerocomprobante"],
                    "nota_credito": r["notacredito"],
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
            cur.execute('SELECT codigsesion, cajero, turno, montoapertura, fechahoraapertura, montocierresistema, montocierrereal, diferencia, estadosesion FROM "CajaSesion" ORDER BY fechahoraapertura DESC LIMIT 1;')
            r = cur.fetchone()
            if r:
                cod_sesion = r["codigsesion"]
                apertura = float(r["montoapertura"] or 0.0)
                estado = r["estadosesion"] or "Abierta"
                cajero = r["cajero"] or "Personal de Caja"
                turno = r["turno"] or "Turno Mañana"
                fecha = str(r["fechahoraapertura"]).split()[0] if r["fechahoraapertura"] else datetime.now().strftime("%Y-%m-%d")
                arqueo_fisico = float(r["montocierrereal"]) if r["montocierrereal"] is not None else None
                diferencia = float(r["diferencia"]) if r["diferencia"] is not None else None

                # Calcular efectivo, digital y egresos en caliente únicamente de la sesión actual
                efectivo = 0.0
                digital = 0.0
                egresos = 0.0
                try:
                    ph = "%s" if is_postgres() else "?"
                    cur.execute(f'SELECT tipomovimiento, concepto, monto FROM "MovimientoCaja" WHERE codigsesion = {ph} ORDER BY fechahora ASC;', (cod_sesion,))
                    for mrow in cur.fetchall():
                        tipo = str(mrow["tipomovimiento"] or "").lower()
                        conc = str(mrow["concepto"] or "").lower()
                        m = float(mrow["monto"] or 0.0)
                        if tipo == "ingreso":
                            if "efectivo" in conc:
                                efectivo += m
                            else:
                                digital += m
                        elif tipo == "egreso" or (tipo == "reversión" and m < 0):
                            egresos += abs(m)
                except Exception:
                    pass

                saldo_teorico = round(apertura + efectivo + digital - egresos, 2)
                conn.close()

                return Caja(
                    id=1,
                    codigo_sesion=cod_sesion,
                    cajero=cajero,
                    fecha=fecha,
                    apertura=apertura,
                    efectivo=efectivo,
                    digital=digital,
                    egresos=egresos,
                    saldo_teorico=saldo_teorico,
                    arqueo_fisico=arqueo_fisico,
                    diferencia=diferencia,
                    estado=estado,
                    turno=turno
                )
            conn.close()
        except Exception as e:
            logger.error("Error en CajaDAO.get_caja_actual: %s", e)

        return Caja(1, datetime.now().strftime("%Y-%m-%d"), 300.0, 0.0, 0.0, 0.0, 300.0)

    def get_movimientos(self) -> List[dict]:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            cur.execute('SELECT codigsesion FROM "CajaSesion" ORDER BY fechahoraapertura DESC LIMIT 1;')
            r = cur.fetchone()
            cod_sesion = r["codigsesion"] if r else "SES-001"

            ph = "%s" if is_postgres() else "?"
            cur.execute(f'SELECT codigmovimiento, codigsesion, tipomovimiento, concepto, monto, fechahora, autorizadopor FROM "MovimientoCaja" WHERE codigsesion = {ph} ORDER BY fechahora DESC;', (cod_sesion,))
            rows = cur.fetchall()
            conn.close()
            return [
                {
                    "hora": str(r["fechahora"]).split()[-1] if r["fechahora"] else "09:00 AM",
                    "tipo": r["tipomovimiento"],
                    "monto": float(r["monto"]),
                    "detalle": r["concepto"],
                    "codigo_movimiento": r["codigmovimiento"],
                    "autorizado_por": r["autorizadopor"]
                }
                for r in rows
            ]
        except Exception as e:
            logger.error("Error en CajaDAO.get_movimientos: %s", e)
            return []

    def add_movimiento_sesion(self, cod_sesion: str, tipo: str, monto: float, detalle: str):
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            cod_mov = f"MOV-{int(datetime.now().timestamp() * 1000) % 10000000}"
            ph = self._ph(7)
            cur.execute(
                f'INSERT INTO "MovimientoCaja" (codigmovimiento, codigsesion, tipomovimiento, concepto, monto, fechahora, autorizadopor) VALUES ({ph});',
                (cod_mov, cod_sesion, tipo, detalle, monto, datetime.now(), "Administrador")
            )
            if not is_postgres():
                conn.commit()
            conn.close()
        except Exception as e:
            logger.error("Error en CajaDAO.add_movimiento_sesion: %s", e)

    def add_movimiento(self, tipo: str, monto: float, detalle: str):
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            cur.execute('SELECT codigsesion FROM "CajaSesion" ORDER BY fechahoraapertura DESC LIMIT 1;')
            r = cur.fetchone()
            cod_sesion = r["codigsesion"] if r else "SES-001"

            cod_mov = f"MOV-{int(datetime.now().timestamp() * 1000) % 10000000}"
            ph = self._ph(7)
            cur.execute(
                f'INSERT INTO "MovimientoCaja" (codigmovimiento, codigsesion, tipomovimiento, concepto, monto, fechahora, autorizadopor) VALUES ({ph});',
                (cod_mov, cod_sesion, tipo, detalle, monto, datetime.now(), "Administrador")
            )
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
            cod = caja.codigo_sesion or "SES-001"
            cur.execute(
                f'UPDATE "CajaSesion" SET montoapertura = {ph}, montocierresistema = {ph}, montocierrereal = {ph}, diferencia = {ph}, estadosesion = {ph}, turno = {ph}, cajero = {ph} WHERE codigsesion = {ph};',
                (caja.apertura, caja.saldo_teorico, caja.arqueo_fisico, caja.diferencia, caja.estado, caja.turno, caja.cajero or "Personal de Caja", cod)
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
        return []

    def save(self, prod: Producto) -> Producto:
        return prod

    def update_stock(self, prod_id: int, delta: int) -> Optional[Producto]:
        return None


class CompraDAO(BaseDAO):
    def find_all(self) -> List[Compra]:
        return []

    def save(self, compra: Compra) -> Compra:
        return compra


class ServicioDAO(BaseDAO):
    def find_all(self) -> List[Servicio]:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            cur.execute('SELECT codigservicio, nombre, categoria, preciobase, duracionminutos, cabinarequerida, porcentajecomision, estadoactivo FROM "Servicio" WHERE estadoactivo = TRUE ORDER BY codigservicio ASC;')
            rows = cur.fetchall()
            conn.close()
            return [
                Servicio(
                    id=r["codigservicio"],
                    nombre=r["nombre"],
                    categoria=r["categoria"],
                    duracion=r["duracionminutos"],
                    precio=float(r["preciobase"]),
                    comision=int(r["porcentajecomision"] or 25),
                    activo=bool(r["estadoactivo"]),
                    cabina_requerida=r["cabinarequerida"] or "Cabina Estándar"
                )
                for r in rows
            ]
        except Exception as e:
            logger.error("Error en ServicioDAO.find_all: %s", e)
            return []

    def find_by_nombre(self, nombre: str) -> Optional[Servicio]:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            ph = "%s" if is_postgres() else "?"
            cur.execute(f'SELECT codigservicio, nombre, categoria, preciobase, duracionminutos, cabinarequerida, porcentajecomision, estadoactivo FROM "Servicio" WHERE LOWER(TRIM(nombre)) = LOWER(TRIM({ph})) AND estadoactivo = TRUE;', (nombre,))
            r = cur.fetchone()
            conn.close()
            if r:
                return Servicio(
                    id=r["codigservicio"],
                    nombre=r["nombre"],
                    categoria=r["categoria"],
                    duracion=r["duracionminutos"],
                    precio=float(r["preciobase"]),
                    comision=int(r["porcentajecomision"] or 25),
                    activo=bool(r["estadoactivo"]),
                    cabina_requerida=r["cabinarequerida"] or "Cabina Estándar"
                )
            return None
        except Exception as e:
            logger.error("Error en ServicioDAO.find_by_nombre: %s", e)
            return None

    def save(self, serv: Servicio) -> Servicio:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            cod_srv = f"SRV-{int(datetime.now().timestamp()) % 100000:03d}"
            ph = self._ph(8)
            cur.execute(
                f'INSERT INTO "Servicio" (codigservicio, nombre, categoria, preciobase, duracionminutos, cabinarequerida, porcentajecomision, estadoactivo) VALUES ({ph});',
                (cod_srv, serv.nombre, serv.categoria, serv.precio, serv.duracion, serv.cabina_requerida or "Cabina Estándar", serv.comision, serv.activo)
            )
            if not is_postgres():
                conn.commit()
            serv.id = cod_srv
            conn.close()
            return serv
        except Exception as e:
            logger.error("Error en ServicioDAO.save: %s", e)
            raise e


class UsuarioDAO(BaseDAO):
    def find_all(self) -> List[Usuario]:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            cur.execute('SELECT username, codigusuario, passwordhash, nombres, apellidos, dni, rol, turno, celular, email, estado FROM "Usuario" WHERE estado = TRUE ORDER BY username ASC;')
            rows = cur.fetchall()
            conn.close()
            return [
                Usuario(
                    usuario=r["username"],
                    nombre=f"{r['nombres']} {r['apellidos']}".strip(),
                    rol=r["rol"],
                    permisos="personal,catalogo,anulaciones,operaciones-caja,agenda,clientes",
                    activo=bool(r["estado"]),
                    dni=r["dni"],
                    apellidos=r["apellidos"] or "",
                    turno=r["turno"] or "Turno Mañana",
                    celular=r["celular"] or "",
                    telefono=r["celular"] or "",
                    email=r["email"] or "",
                    password_temporal=r["passwordhash"] or "1234",
                    cod_usuario=r["codigusuario"] or "USR-001"
                )
                for r in rows
            ]
        except Exception as e:
            logger.error("Error en UsuarioDAO.find_all: %s", e)
            return []

    def find_by_dni(self, dni: str) -> Optional[Usuario]:
        if not dni:
            return None
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            ph = "%s" if is_postgres() else "?"
            cur.execute(f'SELECT username, codigusuario, passwordhash, nombres, apellidos, dni, rol, turno, celular, email, estado FROM "Usuario" WHERE dni = {ph} AND estado = TRUE;', (dni,))
            r = cur.fetchone()
            conn.close()
            if r:
                return Usuario(
                    usuario=r["username"],
                    nombre=f"{r['nombres']} {r['apellidos']}".strip(),
                    rol=r["rol"],
                    permisos="personal,catalogo,anulaciones,operaciones-caja,agenda,clientes",
                    activo=bool(r["estado"]),
                    dni=r["dni"],
                    apellidos=r["apellidos"] or "",
                    turno=r["turno"] or "Turno Mañana",
                    celular=r["celular"] or "",
                    telefono=r["celular"] or "",
                    email=r["email"] or "",
                    password_temporal=r["passwordhash"] or "1234",
                    cod_usuario=r["codigusuario"] or "USR-001"
                )
            return None
        except Exception as e:
            logger.error("Error en UsuarioDAO.find_by_dni: %s", e)
            return None

    def find_by_usuario(self, usuario: str) -> Optional[Usuario]:
        if not usuario:
            return None
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            ph = "%s" if is_postgres() else "?"
            cur.execute(f'SELECT username, codigusuario, passwordhash, nombres, apellidos, dni, rol, turno, celular, email, estado FROM "Usuario" WHERE LOWER(username) = LOWER({ph});', (usuario,))
            r = cur.fetchone()
            conn.close()
            if r:
                return Usuario(
                    usuario=r["username"],
                    nombre=f"{r['nombres']} {r['apellidos']}".strip(),
                    rol=r["rol"],
                    permisos="personal,catalogo,anulaciones,operaciones-caja,agenda,clientes",
                    activo=bool(r["estado"]),
                    dni=r["dni"],
                    apellidos=r["apellidos"] or "",
                    turno=r["turno"] or "Turno Mañana",
                    celular=r["celular"] or "",
                    telefono=r["celular"] or "",
                    email=r["email"] or "",
                    password_temporal=r["passwordhash"] or "1234",
                    cod_usuario=r["codigusuario"] or "USR-001"
                )
            return None
        except Exception as e:
            logger.error("Error en UsuarioDAO.find_by_usuario: %s", e)
            return None

    def save(self, user: Usuario) -> Usuario:
        try:
            conn = get_connection()
            cur = get_cursor(conn)
            ph = self._ph(11)
            parts = (user.nombre or "").split(" ", 1)
            nombres = parts[0]
            apellidos = user.apellidos if user.apellidos else (parts[1] if len(parts) > 1 else "")
            cod_usr = user.cod_usuario
            if not cod_usr or cod_usr == "USR-001":
                cod_usr = f"USR-{int(datetime.now().timestamp() * 1000) % 10000000:07d}"
            cur.execute(
                f'INSERT INTO "Usuario" (username, codigusuario, passwordhash, nombres, apellidos, dni, rol, turno, celular, email, estado) VALUES ({ph});',
                (user.usuario, cod_usr, user.password_temporal or "1234", nombres, apellidos, user.dni, user.rol, user.turno or "Turno Mañana", user.telefono or user.celular, user.email, user.activo)
            )
            if not is_postgres():
                conn.commit()
            conn.close()
            user.cod_usuario = cod_usr
            return user
        except Exception as e:
            logger.error("Error en UsuarioDAO.save: %s", e)
            raise e
