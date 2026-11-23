"""
=============================================================================
CAPA 2: SERVICIOS DE NEGOCIO (REGLAS DEL NEGOCIO - LOGIC LAYER)
Implementa las validaciones, cálculos y reglas de negocio para los RF01 a RF12
Conforme a la Sección 3.8.1 y 3.8.5 del Documento de Arquitectura
=============================================================================
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from models.entities import Cita, Cliente, Venta, Caja, Compra, Servicio
from daos.repositories import (
    ClienteDAO, CitaDAO, VentaDAO, CajaDAO,
    ProductoDAO, CompraDAO, ServicioDAO, UsuarioDAO
)

class CitaService:
    def __init__(self, cita_dao: CitaDAO, cliente_dao: ClienteDAO):
        self.cita_dao = cita_dao
        self.cliente_dao = cliente_dao

    def listar_citas(self) -> List[dict]:
        return [c.to_dict() for c in self.cita_dao.find_all()]

    def agendar_cita(self, data: dict) -> Dict[str, Any]:
        """RF02: Validar disponibilidad en tiempo real y agendar cita."""
        fecha = data.get("fecha", datetime.now().strftime("%Y-%m-%d"))
        hora = data.get("hora", "10:00 AM")
        especialista_raw = data.get("especialista", "Carmen Sánchez")
        especialista = especialista_raw.split("(")[0].strip()
        cliente_nombre = data.get("cliente", "Cliente")
        dni_raw = str(data.get("dni", "")).strip()
        dni = dni_raw if (dni_raw and dni_raw.lower() != "mostrador") else "70000001"
        servicio = data.get("servicio", "Masaje Relajante Aleida")
        monto = float(data.get("monto", 250.0))

        # Regla de Negocio: Validar colisión de horario
        conflicto = self.cita_dao.find_conflict(fecha, hora, especialista)
        if conflicto:
            return {
                "success": False,
                "error": f"Conflicto de horario: {especialista} ya tiene agendada una cita con {conflicto.cliente} a las {hora}.",
                "sugerencia": "Por favor seleccione otro especialista o un bloque horario libre."
            }

        # RF01: Registrar o actualizar cliente automáticamente
        self.cliente_dao.save(Cliente(
            dni=dni,
            nombre=cliente_nombre,
            telefono=data.get("telefono", "987654321"),
            preferencias=data.get("preferencias", "Registrado vía canal web")
        ))

        # Crear y persistir Cita
        nueva_cita = Cita(
            id=0,
            hora=hora,
            fecha=fecha,
            cliente=cliente_nombre,
            dni=dni,
            servicio=servicio,
            especialista=especialista,
            estado="Confirmada",
            monto=monto,
            cobrado=False
        )
        guardada = self.cita_dao.save(nueva_cita)

        return {
            "success": True,
            "message": f"Cita confirmada exitosamente para {cliente_nombre} con {especialista} ({hora}).",
            "cita": guardada.to_dict()
        }

    def obtener_cita(self, cita_id: Any) -> Optional[Dict[str, Any]]:
        """Paso 3 y 4 de CUS Reprogramar Cita: Consultar expediente de cita por código y retornar datos de cita y especialista."""
        cita = self.cita_dao.find_by_id(cita_id)
        if not cita:
            return None
        return cita.to_dict()

    def reprogramar_cita(self, cita_id: Any, nueva_fecha: str, nueva_hora: str) -> Dict[str, Any]:
        """CUS Reprogramar Cita según Diagrama de Secuencia Oficial (Pasos 7 a 15)."""
        cita = self.cita_dao.find_by_id(cita_id)
        if not cita:
            return {"success": False, "error": f"Cita #{cita_id} no encontrada en el sistema.", "status_code": 404}

        # Paso 8: Verificar disponibilidad de especialista
        conflicto = self.cita_dao.find_conflict(nueva_fecha, nueva_hora, cita.especialista)
        if conflicto and str(conflicto.id) != str(cita.id):
            # Paso 14: Notificar conflicto de horario de especialista
            esp_nombre = (cita.especialista or "").split("(")[0].strip()
            return {
                "success": False,
                "paso": 14,
                "error": f"Notificar conflicto de horario de especialista: {esp_nombre} ya cuenta con una cita en el horario {nueva_hora} del {nueva_fecha}.",
                "mensaje": f"Paso 14: Notificar conflicto de horario de especialista: {esp_nombre} ya cuenta con una cita confirmada a las {nueva_hora} del {nueva_fecha}.",
                "alerta": f"Paso 15: Mostrar alerta de horario ocupado en pantalla para {esp_nombre}.",
                "especialista": esp_nombre,
                "nueva_fecha": nueva_fecha,
                "nueva_hora": nueva_hora,
                "status_code": 409
            }

        # Paso 9: Retornar confirmación de horario libre
        # Paso 10: Actualizar fecha y hora de la cita
        cita.fecha = nueva_fecha
        cita.hora = nueva_hora
        cita.estado = "Reprogramada"

        # Paso 11: Confirmar actualización en base de datos
        self.cita_dao.update(cita)

        # Paso 12: Notificar reprogramación exitosa
        return {
            "success": True,
            "paso": 12,
            "message": f"Paso 12: Notificar reprogramación exitosa. Cita reprogramada para el {nueva_fecha} a las {nueva_hora} (Estado: Reprogramada).",
            "cita": cita.to_dict(),
            "status_code": 200
        }

    def cambiar_estado(self, cita_id: Any, nuevo_estado: str, motivo: str = None) -> Dict[str, Any]:
        """CUS04 / CUS05: Actualizar estado (Atendida, Cancelada, etc.) con persistencia en base de datos."""
        cita = self.cita_dao.find_by_id(cita_id)
        if not cita:
            return {"success": False, "error": f"Cita #{cita_id} no encontrada en el sistema.", "status_code": 404}

        if nuevo_estado == "Cancelada" and not motivo:
            return {
                "success": False,
                "error": "Debe especificar un motivo justificado para cancelar la cita y liberar el horario.",
                "status_code": 400
            }

        cita.estado = nuevo_estado
        if motivo:
            cita.motivo_cancelacion = motivo
        self.cita_dao.update(cita)
        
        msg = f"Cita #{cita_id} actualizada a '{nuevo_estado}' en base de datos."
        if nuevo_estado == "Cancelada":
            msg = f"Cita #{cita_id} cancelada exitosamente con motivo: '{motivo}'. Horario y cabina liberados de inmediato en la agenda."
        elif nuevo_estado == "Atendida":
            msg = f"Cita #{cita_id} marcada como 'Atendida'. Cabina liberada y lista para cobro en Caja."

        return {"success": True, "message": msg, "cita": cita.to_dict(), "status_code": 200}


class VentaService:
    def __init__(self, venta_dao: VentaDAO, cita_dao: CitaDAO, caja_dao: CajaDAO):
        self.venta_dao = venta_dao
        self.cita_dao = cita_dao
        self.caja_dao = caja_dao

    def listar_ventas(self) -> List[dict]:
        return [v.to_dict() for v in self.venta_dao.find_all()]

    def liquidar_cita(self, cita_id: Any) -> Dict[str, Any]:
        """
        CUS Procesar Venta y Cobro: Pasos 2, 3 y 4 del Diagrama de Secuencia Oficial BCE:
        2: Solicitar liquidación de cita con estado Atendida (:FormPOS -> :VentaService)
        3: Calcular subtotal e impuesto IGV de atención culminada (:VentaService -> :Venta)
        4: Retornar desglose de importes y total (:Venta -> :VentaService)
        """
        cita = self.cita_dao.find_by_id(cita_id)
        if not cita:
            return {
                "success": False,
                "error": f"Cita #{cita_id} no encontrada para liquidación.",
                "status_code": 404
            }

        total = float(cita.monto or 0.0)
        subtotal = round(total / 1.18, 2)
        igv = round(total - subtotal, 2)

        return {
            "success": True,
            "paso": 4,
            "cita_id": str(cita.id),
            "cliente": cita.cliente,
            "dni": cita.dni,
            "servicio": cita.servicio,
            "especialista": cita.especialista,
            "estado": cita.estado,
            "subtotal": subtotal,
            "igv": igv,
            "total": total,
            "desglose": {
                "base_imponible": subtotal,
                "igv_18": igv,
                "total_a_pagar": total
            },
            "mensaje": f"Paso 4: Retornar desglose de importes y total (Subtotal: S/ {subtotal:.2f}, IGV: S/ {igv:.2f}, Total: S/ {total:.2f})."
        }

    def procesar_venta(self, data: dict) -> Dict[str, Any]:
        """
        CUS Procesar Venta y Cobro según Diagrama de Secuencia Oficial BCE:
        8: Validar pago conforme y caja abierta (:FormPOS -> :VentaService)
        [Pago Conforme y Caja Abierta]:
        9: Registrar venta y numero de boleta (:VentaService -> :Venta)
        10: Confirmar registro y actualizar cita (:Venta -> :VentaService)
        11: Notificar venta procesada con exito (:VentaService -> :FormPOS)
        12: Mostrar boleta de venta para imprimir (:FormPOS -> :Cajero)
        [Monto Insuficiente o Pago Invalido]:
        13: Notificar importe menor al total a pagar (:VentaService -> :FormPOS)
        14: Mostrar alerta de saldo insuficiente en pantalla (:FormPOS -> :Cajero)
        """
        # Paso 8: Validar caja abierta
        caja = self.caja_dao.get_caja_actual()
        if str(caja.estado).strip().lower() != "abierta":
            return {
                "success": False,
                "paso": 8,
                "error": "Paso 8: Validación fallida - La caja de turno no se encuentra abierta. Debe aperturar caja antes de procesar cobros.",
                "mensaje": "Paso 8: La caja se encuentra cerrada. Debe aperturar el turno en el módulo de Caja.",
                "status_code": 400
            }

        total_base = float(data.get("monto", 0.0))
        descuento = float(data.get("descuento", 0.0))
        total_neto = max(0.0, round(total_base - descuento, 2))

        # Paso 8: Validar pago conforme (monto ingresado >= total a pagar)
        monto_ingresado_raw = data.get("monto_ingresado", data.get("pago", data.get("monto_pagado", total_neto)))
        try:
            monto_ingresado = float(monto_ingresado_raw)
        except (ValueError, TypeError):
            monto_ingresado = 0.0

        if monto_ingresado < total_neto:
            # Paso 13: Notificar importe menor al total a pagar
            faltante = round(total_neto - monto_ingresado, 2)
            return {
                "success": False,
                "paso": 13,
                "error": f"Paso 13: Notificar importe menor al total a pagar. Monto ingresado S/ {monto_ingresado:.2f} es insuficiente para cubrir el total de S/ {total_neto:.2f}.",
                "mensaje": f"Paso 13: Notificar importe menor al total a pagar (Faltan S/ {faltante:.2f}).",
                "alerta": f"Paso 14: Mostrar alerta de saldo insuficiente en pantalla (Faltan S/ {faltante:.2f}).",
                "monto_ingresado": monto_ingresado,
                "total_neto": total_neto,
                "faltante": faltante,
                "status_code": 400
            }

        cliente = data.get("cliente", "Cliente General")
        dni_cliente = data.get("dni", "72819382")
        servicio = data.get("servicio", "Servicio Spa")
        medio_pago = data.get("medio_pago", "Efectivo")
        cita_id = data.get("cita_id")

        # Regla Tributaria SUNAT: Desglose de IGV 18%
        subtotal = round(total_neto / 1.18, 2)
        igv = round(total_neto - subtotal, 2)

        # Paso 9: Registrar venta y numero de boleta (:VentaService -> :Venta)
        num_boleta = f"B001-{len(self.venta_dao.find_all()) + 4821:07d}"

        nueva_venta = Venta(
            id=0,
            numero_boleta=num_boleta,
            fecha=datetime.now().strftime("%Y-%m-%d %H:%M"),
            cliente=cliente,
            dni_cliente=dni_cliente,
            servicio=servicio,
            subtotal=subtotal,
            igv=igv,
            descuento=descuento,
            total=total_neto,
            medio_pago=medio_pago,
            estado="Emitida"
        )
        guardada = self.venta_dao.save(nueva_venta)

        # Paso 10: Confirmar registro y actualizar cita (:Venta -> :VentaService)
        cita_actualizada = None
        if cita_id:
            c = self.cita_dao.find_by_id(cita_id)
            if c:
                c.cobrado = True
                c.estado = "Cobrada"
                c.observaciones = f"{c.servicio} · Cobrado con Boleta {num_boleta}"
                self.cita_dao.update(c)
                cita_actualizada = c.to_dict()

        if not cita_actualizada:
            for c in self.cita_dao.find_all():
                if (c.cliente.lower() == cliente.lower() or (c.dni and c.dni == dni_cliente)) and not c.cobrado:
                    c.cobrado = True
                    c.estado = "Cobrada"
                    c.observaciones = f"{c.servicio} · Cobrado con Boleta {num_boleta}"
                    self.cita_dao.update(c)
                    cita_actualizada = c.to_dict()
                    break

        # Actualizar balances de caja e insertar movimiento de ingreso
        if "efectivo" in medio_pago.lower():
            caja.efectivo += total_neto
        else:
            caja.digital += total_neto
        caja.saldo_teorico = round(float(caja.apertura) + float(caja.efectivo) + float(caja.digital) - float(caja.egresos), 2)
        self.caja_dao.update_caja(caja)

        self.caja_dao.add_movimiento(
            tipo="Ingreso",
            monto=total_neto,
            detalle=f"Cobro Boleta {num_boleta} ({medio_pago}) - {cliente}"
        )

        caja_dict = caja.to_dict()
        caja_dict["total_teorico"] = caja.saldo_teorico

        # Paso 11: Notificar venta procesada con exito (:VentaService -> :FormPOS)
        # Paso 12: Mostrar boleta de venta para imprimir (:FormPOS -> :Cajero)
        vuelto = round(max(0.0, monto_ingresado - total_neto), 2) if "efectivo" in medio_pago.lower() else 0.0

        return {
            "success": True,
            "paso": 11,
            "message": f"Paso 11: Notificar venta procesada con éxito. Boleta {num_boleta} emitida por S/ {total_neto:.2f}.",
            "confirmacion": f"Paso 10: Venta {num_boleta} confirmada en base de datos y cita de {cliente} actualizada a 'Cobrada'.",
            "alerta": "Paso 12: Mostrar boleta de venta para imprimir.",
            "boleta": {
                "numero_boleta": num_boleta,
                "serie": "B001",
                "cliente": cliente,
                "dni_cliente": dni_cliente,
                "servicio": servicio,
                "subtotal": subtotal,
                "igv": igv,
                "total": total_neto,
                "medio_pago": medio_pago,
                "monto_ingresado": monto_ingresado,
                "vuelto": vuelto,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
            },
            "venta": guardada.to_dict(),
            "cita": cita_actualizada,
            "caja": caja_dict,
            "vuelto": vuelto,
            "status_code": 201
        }

    def anular_venta(self, data: dict) -> Dict[str, Any]:
        """RF06: Anulación controlada con motivo obligatorio, PIN gerencial y Nota de Crédito."""
        pin = str(data.get("pin", "")).strip()
        if pin != "1234":
            return {"success": False, "error": "Acceso denegado: PIN de autorización gerencial incorrecto (requiere PIN 1234)."}

        boleta = str(data.get("boleta", "")).strip()
        motivo = str(data.get("motivo", "")).strip()
        if not motivo:
            return {"success": False, "error": "Debe especificar el motivo obligatorio de anulación."}

        # Buscar venta registrada si existe para heredar datos fiscales
        venta = self.venta_dao.find_by_ticket(boleta) if boleta else None
        monto = float(data.get("monto", venta.total if venta else 280.0))
        cliente = data.get("cliente", venta.cliente if venta else "Cliente General")
        medio_pago = data.get("medio_pago", venta.medio_pago if venta else "Digital")

        nc_num = f"NC-{len(self.venta_dao.get_anulaciones()) + 13:03d}"

        anulacion = {
            "boleta": boleta or f"B001-{len(self.venta_dao.get_anulaciones()) + 4820}",
            "nota_credito": nc_num,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "monto": monto,
            "motivo": motivo,
            "autorizado_por": data.get("autorizado_por", "Aleida Mendoza (Gerente General)"),
            "cliente": cliente
        }
        self.venta_dao.save_anulacion(anulacion)

        # Actualizar estado de la venta en base de datos
        if boleta:
            self.venta_dao.update_estado_anulada(boleta, nc_num)

        # Reversión contable en caja según medio de pago (CU04 & CU05)
        caja = self.caja_dao.get_caja_actual()
        if "efectivo" in medio_pago.lower():
            caja.efectivo = max(0.0, float(caja.efectivo) - monto)
        else:
            caja.digital = max(0.0, float(caja.digital) - monto)

        caja.saldo_teorico = round(float(caja.apertura) + float(caja.efectivo) + float(caja.digital) - float(caja.egresos), 2)
        self.caja_dao.update_caja(caja)

        self.caja_dao.add_movimiento(
            tipo="Reversión",
            monto=-monto,
            detalle=f"Anulación de Boleta {boleta} mediante {nc_num} ({motivo})"
        )

        caja_dict = caja.to_dict()
        caja_dict["total_teorico"] = caja.saldo_teorico

        return {
            "success": True,
            "message": f"Anulación autorizada por Gerencia. Se emitió la Nota de Crédito {nc_num} por S/ {monto:.2f} y se reversó el importe en caja.",
            "anulacion": anulacion,
            "caja": caja_dict
        }


class CajaService:
    def __init__(self, caja_dao: CajaDAO):
        self.caja_dao = caja_dao

    def obtener_estado_caja(self) -> Dict[str, Any]:
        """
        CUS Apertura Turno de Caja (Pasos 2, 3, 4, 13, 14):
        2: Solicitar estado actual de la caja (:FormCaja -> :CajaService)
        3: Consultar sesion de caja en base de datos (:CajaService -> :Caja)
        [Caja NO Aperturada en el Turno]:
        4: Retornar caja no aperturada en el turno (:Caja -> :CajaService)
        [Caja Ya Aperturada en el Turno]:
        13: Retornar turno activo con estado abierta (:Caja -> :CajaService)
        14: Notificar sesion de caja ya iniciada (:CajaService -> :FormCaja)
        """
        caja = self.caja_dao.get_caja_actual()
        caja_dict = caja.to_dict()
        total = round(float(caja.apertura) + float(caja.efectivo) + float(caja.digital) - float(caja.egresos), 2)
        caja_dict["saldo_teorico"] = total
        caja_dict["total_teorico"] = total

        caja_abierta = (str(caja.estado).strip().lower() == "abierta")

        res = {
            **caja_dict,
            "caja_abierta": caja_abierta,
            "estado": caja.estado,
            "estadosesion": caja.estado,
            "movimientos": self.caja_dao.get_movimientos()
        }

        if caja_abierta:
            # Paso 13 y 14: Caja Ya Aperturada en el Turno
            res["paso"] = 14
            res["mensaje"] = f"Paso 14: Notificar sesión de caja ya iniciada ({caja.turno} con estado {caja.estado})."
            res["alerta"] = "Paso 15: Mostrar caja activa y continuar con cobros."
        else:
            # Paso 4 y 5: Caja NO Aperturada en el Turno
            res["paso"] = 4
            res["mensaje"] = "Paso 4: Retornar caja no aperturada en el turno."
            res["alerta"] = "Paso 5: Habilitar formulario de apertura."

        return res

    def aperturar_caja(self, apertura_data: dict) -> Dict[str, Any]:
        """
        CUS Apertura Turno de Caja (Pasos 8, 9, 10, 11, 12):
        8: Validar monto de fondo no negativo (:FormCaja -> :CajaService)
        9: Registrar apertura de caja con estado abierta (:CajaService -> :Caja)
        10: Confirmar apertura en base de datos (:Caja -> :CajaService)
        11: Notificar apertura de turno exitosa (:CajaService -> :FormCaja)
        """
        try:
            monto_val = apertura_data.get("saldo_inicial", apertura_data.get("monto", 0.0))
            monto_inicial = float(monto_val)
        except (ValueError, TypeError):
            monto_inicial = -1.0

        # Paso 8: Validar monto de fondo no negativo (:FormCaja -> :CajaService)
        if monto_inicial < 0:
            return {
                "success": False,
                "paso": 8,
                "error": "Paso 8: Validación fallida - El monto de fondo inicial no puede ser negativo (monto ≥ 0).",
                "mensaje": "Paso 8: Validar monto de fondo no negativo: El monto de fondo inicial no puede ser negativo.",
                "status_code": 400
            }

        turno = apertura_data.get("turno", "Turno Mañana")
        responsable = apertura_data.get("responsable", "Personal de Mostrador")
        observaciones = apertura_data.get("observaciones", "Fondo de sencillo inicial verificado en billetes y monedas")

        cod_sesion = f"SES-{int(datetime.now().timestamp()) % 1000000:06d}"
        now_dt = datetime.now()

        # Paso 9: Registrar apertura de caja con estado abierta (:CajaService -> :Caja)
        # Paso 10: Confirmar apertura en base de datos (:Caja -> :CajaService)
        from database import get_connection, get_cursor, is_postgres
        conn = get_connection()
        cur = get_cursor(conn)
        ph = "%s" if is_postgres() else "?"
        cur.execute(
            f'INSERT INTO "CajaSesion" (codigsesion, cajero, turno, montoapertura, fechahoraapertura, montocierresistema, estadosesion) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph});',
            (cod_sesion, responsable, turno, monto_inicial, now_dt, monto_inicial, "Abierta")
        )
        if not is_postgres():
            conn.commit()
        conn.close()

        self.caja_dao.add_movimiento_sesion(
            cod_sesion=cod_sesion,
            tipo="Apertura",
            monto=monto_inicial,
            detalle=f"Fondo de sencillo inicial ({turno}) por {responsable}. {observaciones}"
        )

        caja = self.caja_dao.get_caja_actual()
        caja_dict = caja.to_dict()
        caja_dict["total_teorico"] = caja.saldo_teorico

        # Paso 11: Notificar apertura de turno exitosa (:CajaService -> :FormCaja)
        return {
            "success": True,
            "paso": 11,
            "message": f"Paso 11: Notificar apertura de turno exitosa. {turno} aperturado exitosamente con fondo inicial de S/ {monto_inicial:.2f}.",
            "confirmacion": f"Paso 11: Apertura de turno '{turno}' confirmada en base de datos con estado Abierta.",
            "alerta": "Paso 12: Mostrar panel de caja habilitado para cobros.",
            "caja": caja_dict,
            "status_code": 201
        }

    def registrar_egreso(self, monto: float, motivo: str) -> Dict[str, Any]:
        """RF07: Salidas de dinero justificadas."""
        if monto <= 0:
            return {"success": False, "error": "El monto del egreso debe ser mayor a 0."}

        caja = self.caja_dao.get_caja_actual()
        caja.egresos += monto
        caja.saldo_teorico = round(float(caja.apertura) + float(caja.efectivo) + float(caja.digital) - float(caja.egresos), 2)
        self.caja_dao.update_caja(caja)

        self.caja_dao.add_movimiento("Egreso", -monto, motivo)
        caja_dict = caja.to_dict()
        caja_dict["total_teorico"] = caja.saldo_teorico
        return {"success": True, "message": f"Egreso de S/ {monto:.2f} registrado ({motivo}).", "caja": caja_dict}

    def realizar_arqueo_y_cierre(self, conteo_fisico: float, responsable: str = None) -> Dict[str, Any]:
        """RF08: Arqueo comparando efectivo físico vs sistema y emisión de Reporte Z."""
        caja = self.caja_dao.get_caja_actual()
        saldo_sistema = round(float(caja.apertura) + float(caja.efectivo) + float(caja.digital) - float(caja.egresos), 2)
        diferencia = round(conteo_fisico - saldo_sistema, 2)

        caja.saldo_teorico = saldo_sistema
        caja.arqueo_fisico = conteo_fisico
        caja.diferencia = diferencia
        caja.estado = "Cerrada"
        self.caja_dao.update_caja(caja)

        self.caja_dao.add_movimiento(
            tipo="Cierre",
            monto=0.0,
            detalle=f"Arqueo y Cierre ({caja.turno}). Físico: S/ {conteo_fisico:.2f}, Dif: S/ {diferencia:+.2f}"
        )

        estado_conformidad = "Caja Cuadrada Conforme (100%)" if abs(diferencia) < 0.50 else f"Discrepancia detectada: S/ {diferencia:+.2f}"

        reporte_z = {
            "numero_reporte": f"Z-2026-{datetime.now().strftime('%m%d%H%M')}",
            "fecha_cierre": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "turno": caja.turno,
            "responsable": responsable or "Personal de Caja",
            "fondo_apertura": caja.apertura,
            "total_efectivo": caja.efectivo,
            "total_digital": caja.digital,
            "total_egresos": caja.egresos,
            "saldo_teorico_sistema": saldo_sistema,
            "conteo_fisico_arqueado": conteo_fisico,
            "diferencia": diferencia,
            "resultado": estado_conformidad,
            "cumplimiento_objetivo_02": "Cumplido (≥ 98% exactitud)" if abs(diferencia) < 0.50 else "Alerta de auditoría"
        }

        caja_dict = caja.to_dict()
        caja_dict["saldo_teorico"] = saldo_sistema
        caja_dict["total_teorico"] = saldo_sistema

        return {
            "success": True,
            "message": f"Arqueo de fin de turno concluido. {estado_conformidad}.",
            "reporte_z": reporte_z,
            "caja": caja_dict
        }


class ReporteService:
    def __init__(self, cita_dao: CitaDAO, venta_dao: VentaDAO, caja_dao: CajaDAO):
        self.cita_dao = cita_dao
        self.venta_dao = venta_dao
        self.caja_dao = caja_dao

    def obtener_metricas_completas(self) -> Dict[str, Any]:
        """RF12: Consolidación de reportes gerenciales con los 4 objetivos realistas SMART."""
        caja = self.caja_dao.get_caja_actual()
        citas = self.cita_dao.find_all()
        ventas = self.venta_dao.find_all()

        total_ingresos = caja.efectivo + caja.digital
        citas_atendidas = len([c for c in citas if c.estado == "Atendida" or c.cobrado])

        return {
            "periodo": "Octubre 2026",
            "objetivos_smart": [
                {
                    "codigo": "OBJ-01",
                    "nombre": "Puntualidad en Citas y Reducción de No-Shows",
                    "meta": "≥ 88%",
                    "actual": "88.5%",
                    "estado": "Cumplido (+0.5%)",
                    "formula": "(Citas a tiempo / Total) * 100",
                    "detalle": "Reducción del 35% en inasistencias mediante recordatorios web."
                },
                {
                    "codigo": "OBJ-02",
                    "nombre": "Exactitud en Arqueos y Cuadre de Caja",
                    "meta": "≥ 98%",
                    "actual": "98.2%",
                    "estado": "Cumplido (+0.2%)",
                    "formula": "(Días sin descuadre / Días del mes) * 100",
                    "detalle": "Disminución del 90% en discrepancias entre efectivo físico y sistema."
                },
                {
                    "codigo": "OBJ-03",
                    "nombre": "Disponibilidad de Insumos Críticos",
                    "meta": "≥ 95%",
                    "actual": "96.5%",
                    "estado": "Cumplido (+1.5%)",
                    "formula": "(Servicios sin quiebre / Total) * 100",
                    "detalle": "Reducción del 80% en tratamientos cancelados por falta de tinte o keratina."
                },
                {
                    "codigo": "OBJ-04",
                    "nombre": "Fidelización y Recompra de Clientes",
                    "meta": "≥ 70%",
                    "actual": "74.0%",
                    "estado": "Cumplido (+4.0%)",
                    "formula": "(Retorno < 45d / Total atendidas) * 100",
                    "detalle": "Incremento del 25% en clientas que regresan en menos de 45 días."
                }
            ],
            "resumen_financiero": {
                "total_facturado": total_ingresos,
                "total_citas_atendidas": citas_atendidas,
                "promedio_ticket": round(total_ingresos / max(1, len(ventas)), 2),
                "total_comprobantes": len(ventas)
            }
        }


# =============================================================================
# CONTROL: CatalogoService (CUS Registrar Servicio en Catálogo)
# Actor: :Administrador | Límite: :FormServicio | Control: :CatalogoService | Entidad: :Servicio
# =============================================================================
class CatalogoService:
    def __init__(self, servicio_dao: ServicioDAO):
        self.servicio_dao = servicio_dao

    def obtener_categorias(self) -> List[str]:
        """Paso 3 y 4 del Diagrama de Secuencia: Cargar categorías de tratamientos y retornar categorías activas del spa."""
        return [
            "Spa & Bienestar",
            "Cosmiatría Facial",
            "Cuidado Capilar",
            "Manos & Pies",
            "Masajes & Cromoterapia",
            "Tratamientos Corporales"
        ]

    def listar_servicios(self) -> List[dict]:
        return [s.to_dict() for s in self.servicio_dao.find_all()]

    def registrar_servicio(self, data: dict) -> Dict[str, Any]:
        """
        CUS Registrar Servicio en Catálogo según Diagrama de Secuencia Oficial BCE:
        - Paso 8: Validar datos y tarifa positiva
        - Paso 9: Verificar no duplicidad de servicio
        - [Datos Válidos y Tarifa Positiva]: Pasos 10-13 (Guardar en BD, confirmar y mostrar)
        - [Tarifa Inválida o Campos Incompletos]: Pasos 14-15 (Notificar error y mostrar alerta)
        """
        nombre = str(data.get("nombre", "")).strip()
        categoria = str(data.get("categoria", "Spa & Bienestar")).strip()
        cabina = str(data.get("cabina", "Cabina Estándar")).strip()
        comision = float(data.get("comision", 25.0))

        # Paso 8: Validar datos y tarifa positiva
        try:
            precio = float(data.get("precio", 0.0))
            duracion = int(data.get("duracion", 0))
        except (ValueError, TypeError):
            # Paso 14: Notificar error de validación de tarifa o duración
            return {
                "success": False,
                "paso": 14,
                "error": "Notificar error de validación de tarifa o duración: La tarifa (precio) y la duración deben ser valores numéricos válidos mayores a cero.",
                "mensaje": "Paso 14: Notificar error de validación de tarifa o duración",
                "alerta": "Paso 15: Mostrar alerta de datos inválidos en pantalla. Ingrese una tarifa mayor a 0 y duración válida.",
                "status_code": 400
            }

        if not nombre or precio <= 0 or duracion <= 0:
            # Paso 14: Notificar error de validación de tarifa o duración
            return {
                "success": False,
                "paso": 14,
                "error": "Notificar error de validación de tarifa o duración: El nombre es obligatorio, y tanto la tarifa como la duración deben ser positivas mayores a cero.",
                "mensaje": "Paso 14: Notificar error de validación de tarifa o duración",
                "alerta": "Paso 15: Mostrar alerta de datos inválidos en pantalla. Verifique que la tarifa y duración sean mayores a 0.",
                "status_code": 400
            }

        # Paso 9: Verificar no duplicidad de servicio
        existente = self.servicio_dao.find_by_nombre(nombre)
        if existente:
            # Paso 14: Notificar error de validación
            return {
                "success": False,
                "paso": 14,
                "error": f"Notificar rechazo por duplicidad: Ya existe un servicio registrado con el nombre '{nombre}' en el catálogo del spa.",
                "mensaje": f"Paso 14: Notificar rechazo por duplicidad de servicio: '{nombre}' ya se encuentra registrado.",
                "alerta": f"Paso 15: Mostrar alerta de datos inválidos en pantalla: El servicio '{nombre}' ya existe.",
                "status_code": 409
            }

        # → [Datos Válidos y Tarifa Positiva]:
        # Paso 10: Guardar nuevo servicio en base de datos
        nuevo = Servicio(
            codigservicio="",
            nombre=nombre,
            categoria=categoria,
            preciobase=precio,
            duracionminutos=duracion,
            cabinarequerida=cabina,
            porcentajecomision=comision,
            estadoactivo=True
        )

        try:
            guardado = self.servicio_dao.save(nuevo)
            # Paso 11: Confirmar almacenamiento en catálogo
            # Paso 12: Notificar servicio registrado con éxito
            return {
                "success": True,
                "paso": 12,
                "message": f"Paso 12: Notificar servicio registrado con éxito: '{nombre}' (Tarifa S/ {precio:.2f}) almacenado en catálogo.",
                "confirmacion": "Confirmar almacenamiento en catálogo oficial",
                "servicio": guardado.to_dict(),
                "status_code": 201
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error al guardar servicio en base de datos: {str(e)}",
                "status_code": 500
            }
