"""
=============================================================================
CAPA 3: ACCESO A DATOS (PATRÓN DAO / REPOSITORIOS)
Implementa el acceso, consulta y persistencia de las entidades
Conforme a la Sección 3.8.2 del Documento de Arquitectura
=============================================================================
"""

from typing import List, Optional
from datetime import datetime
from models.entities import Cliente, Cita, Servicio, Producto, Venta, Caja, Compra, Proveedor, Usuario

class ClienteDAO:
    def __init__(self):
        self._clientes = [
            Cliente("72819382", "Mariana Torres", "987654321", "Piel mixta, prefiere aromaterapia de lavanda.", 12, "2026-10-06"),
            Cliente("45910284", "Patricia Valdivia", "945112233", "Sensibilidad a tintes con amoníaco.", 8, "2026-10-06"),
            Cliente("48192039", "Claudia Morales", "912345678", "Tratamiento keratina semestral.", 5, "2026-10-06"),
            Cliente("70829104", "Jessica Rivas", "923456789", "Manicura semipermanente color nude.", 3, "2026-10-05")
        ]

    def find_all(self) -> List[Cliente]:
        return self._clientes

    def find_by_dni(self, dni: str) -> Optional[Cliente]:
        for c in self._clientes:
            if c.dni == dni:
                return c
        return None

    def save(self, cliente: Cliente) -> Cliente:
        existing = self.find_by_dni(cliente.dni)
        if existing:
            existing.nombre = cliente.nombre
            existing.telefono = cliente.telefono
            existing.preferencias = cliente.preferencias
            existing.visitas += 1
            existing.ultima_visita = datetime.now().strftime("%Y-%m-%d")
            return existing
        self._clientes.append(cliente)
        return cliente

class CitaDAO:
    def __init__(self):
        self._citas = [
            Cita(1, "09:00 AM", "2026-10-06", "Mariana Torres", "72819382", "Masaje Relajante Aleida", "Carmen Sánchez", "Atendida", 280.0, True),
            Cita(2, "10:30 AM", "2026-10-06", "Patricia Valdivia", "45910284", "Facial Rejuvenecedor con Oro", "Carmen Sánchez", "Confirmada", 450.0, False),
            Cita(3, "11:45 AM", "2026-10-06", "Claudia Morales", "48192039", "Tratamiento Capilar Keratina", "Luisa Paredes", "En Atención", 350.0, False),
            Cita(4, "02:30 PM", "2026-10-06", "Jessica Rivas", "70829104", "Manicura Spa Premium", "Ana Vargas", "Pendiente", 150.0, False)
        ]

    def find_all(self) -> List[Cita]:
        return self._citas

    def find_by_id(self, cita_id: int) -> Optional[Cita]:
        for c in self._citas:
            if c.id == cita_id:
                return c
        return None

    def find_conflict(self, fecha: str, hora: str, especialista: str) -> Optional[Cita]:
        for c in self._citas:
            if c.fecha == fecha and c.hora == hora and c.especialista == especialista and c.estado not in ["Cancelada", "No Asistió"]:
                return c
        return None

    def save(self, cita: Cita) -> Cita:
        cita.id = len(self._citas) + 1
        self._citas.append(cita)
        return cita

    def update(self, cita: Cita) -> Cita:
        for i, c in enumerate(self._citas):
            if c.id == cita.id:
                self._citas[i] = cita
                return cita
        return cita

class VentaDAO:
    def __init__(self):
        self._ventas = [
            Venta(1, "B001-0004820", "2026-10-06 09:45", "Mariana Torres", "Masaje Relajante Aleida", 237.29, 42.71, 0.0, 280.0, "Efectivo", "Emitida")
        ]
        self._anulaciones = [
            {"id": 1, "fecha": "2026-10-05 16:30", "boleta": "B001-0004810", "nota_credito": "NC-012", "monto": 120.0, "motivo": "Devolución por insatisfacción", "autorizado_por": "Aleida Mendoza (Gerente)"}
        ]

    def find_all(self) -> List[Venta]:
        return self._ventas

    def find_by_ticket(self, numero_boleta: str) -> Optional[Venta]:
        for v in self._ventas:
            if v.numero_boleta == numero_boleta:
                return v
        return None

    def save(self, venta: Venta) -> Venta:
        venta.id = len(self._ventas) + 1
        self._ventas.append(venta)
        return venta

    def save_anulacion(self, anulacion_data: dict) -> dict:
        anulacion_data["id"] = len(self._anulaciones) + 1
        self._anulaciones.append(anulacion_data)
        return anulacion_data

    def get_anulaciones(self) -> List[dict]:
        return self._anulaciones

class CajaDAO:
    def __init__(self):
        self._caja = Caja(1, datetime.now().strftime("%Y-%m-%d"), 150.0, 720.0, 1580.0, 45.0, 2405.0)
        self._movimientos = [
            {"hora": "08:30 AM", "tipo": "Apertura", "monto": 150.0, "detalle": "Fondo de sencillo inicial (RF07)"},
            {"hora": "09:45 AM", "tipo": "Ingreso", "monto": 280.0, "detalle": "Cobro Boleta B001-4820 en Efectivo (RF05)"},
            {"hora": "11:00 AM", "tipo": "Egreso", "monto": -45.0, "detalle": "Salida menor por refrigerio de colaboradores (RF07)"},
            {"hora": "11:30 AM", "tipo": "Ingreso", "monto": 450.0, "detalle": "Cobro Boleta B001-4821 vía Yape (RF05)"},
            {"hora": "01:15 PM", "tipo": "Ingreso", "monto": 350.0, "detalle": "Cobro Boleta B001-4822 con Tarjeta POS (RF05)"}
        ]

    def get_caja_actual(self) -> Caja:
        self._caja.saldo_teorico = self._caja.apertura + self._caja.efectivo + self._caja.digital - self._caja.egresos
        return self._caja

    def get_movimientos(self) -> List[dict]:
        return self._movimientos

    def add_movimiento(self, tipo: str, monto: float, detalle: str):
        self._movimientos.append({
            "hora": datetime.now().strftime("%I:%M %p"),
            "tipo": tipo,
            "monto": monto,
            "detalle": detalle
        })

    def update_caja(self, caja: Caja) -> Caja:
        self._caja = caja
        return self._caja

class ProductoDAO:
    def __init__(self):
        self._productos = [
            Producto(1, "Tinte Profesional 6.1 (Cenizo)", "L'Oréal Professionnel Perú", 2, 6, 28.0, 45.0, True),
            Producto(2, "Crema Nutritiva Keratina 1L", "Distribuidora Belleza Total SAC", 1, 4, 85.0, 130.0, True),
            Producto(3, "Aceite de Argán Puro 250ml", "BioCosmetics Natura", 8, 3, 35.0, 60.0, False)
        ]

    def find_all(self) -> List[Producto]:
        return self._productos

    def save(self, prod: Producto) -> Producto:
        prod.id = len(self._productos) + 1
        self._productos.append(prod)
        return prod

    def update_stock(self, prod_id: int, delta: int) -> Optional[Producto]:
        for p in self._productos:
            if p.id == prod_id:
                p.stock += delta
                p.alerta = p.stock <= p.stock_min
                return p
        return None

class CompraDAO:
    def __init__(self):
        self._compras = [
            Compra(1, "OC-2026-088", "2026-10-05", "L'Oréal Professionnel Perú", "Tinte Profesional 6.1 (12 unidades)", 12, 336.0, "En Tránsito")
        ]

    def find_all(self) -> List[Compra]:
        return self._compras

    def save(self, compra: Compra) -> Compra:
        compra.id = len(self._compras) + 1
        self._compras.append(compra)
        return compra

class ServicioDAO:
    def __init__(self):
        self._servicios = [
            Servicio(1, "Masaje Relajante Aleida", "Spa & Bienestar", 90, 280.0, 25, True),
            Servicio(2, "Facial Rejuvenecedor con Oro", "Cosmiatría Facial", 75, 450.0, 30, True),
            Servicio(3, "Tratamiento Capilar Keratina", "Cuidado Capilar", 120, 350.0, 30, True),
            Servicio(4, "Manicura Spa Premium", "Manos & Pies", 60, 150.0, 35, True)
        ]

    def find_all(self) -> List[Servicio]:
        return self._servicios

    def save(self, serv: Servicio) -> Servicio:
        serv.id = len(self._servicios) + 1
        self._servicios.append(serv)
        return serv

class UsuarioDAO:
    def __init__(self):
        self._usuarios = [
            Usuario("cramos", "Camila Ramos", "Recepcionista", "Agenda (CU01), Clientes (CU02), POS (CU03)"),
            Usuario("aleida_admin", "Aleida Mendoza", "Gerente General", "Acceso Total (CU01-CU09), Aprobación de Anulaciones (CU04)"),
            Usuario("csanchez", "Carmen Sánchez", "Terapeuta / Cosmiatra", "Consulta de Agenda propia, Historial de atenciones")
        ]

    def find_all(self) -> List[Usuario]:
        return self._usuarios

    def save(self, user: Usuario) -> Usuario:
        self._usuarios.append(user)
        return user
