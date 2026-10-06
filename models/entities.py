"""
=============================================================================
CAPA 4: BASE DE DATOS Y ENTIDADES DE NEGOCIO (MODELOS)
Define las 8 Entidades de Negocio del Sistema de Salon Spa Aleida
Conforme a la Sección 3.8.1 y 3.8.2 del Documento de Arquitectura
=============================================================================
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, List
from datetime import datetime

@dataclass
class Cliente:
    dni: str
    nombre: str
    telefono: str
    preferencias: str
    visitas: int = 1
    ultima_visita: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

    def to_dict(self):
        return asdict(self)

@dataclass
class Cita:
    id: int
    hora: str
    fecha: str
    cliente: str
    dni: str
    servicio: str
    especialista: str
    estado: str = "Confirmada"  # Confirmada, En Atención, Atendida, Cancelada, No Asistió
    monto: float = 0.0
    cobrado: bool = False
    motivo_cancelacion: Optional[str] = None

    def to_dict(self):
        return asdict(self)

@dataclass
class Servicio:
    id: int
    nombre: str
    categoria: str
    duracion: int  # minutos
    precio: float
    comision: int  # porcentaje
    activo: bool = True

    def to_dict(self):
        return asdict(self)

@dataclass
class Producto:
    id: int
    nombre: str
    proveedor: str
    stock: int
    stock_min: int
    costo: float
    precio_venta: float
    alerta: bool = False

    def to_dict(self):
        return asdict(self)

@dataclass
class Venta:
    id: int
    numero_boleta: str
    fecha: str
    cliente: str
    servicio: str
    subtotal: float
    igv: float
    descuento: float
    total: float
    medio_pago: str  # Efectivo, Tarjeta POS, Yape/Plin, Mixto
    estado: str = "Emitida"  # Emitida, Anulada
    nota_credito: Optional[str] = None

    def to_dict(self):
        return asdict(self)

@dataclass
class Caja:
    id: int
    fecha: str
    apertura: float
    efectivo: float
    digital: float
    egresos: float
    saldo_teorico: float
    arqueo_fisico: Optional[float] = None
    diferencia: Optional[float] = None
    estado: str = "Abierta"  # Abierta, Cerrada
    turno: str = "Turno Mañana"

    def to_dict(self):
        return asdict(self)

@dataclass
class Compra:
    id: int
    numero_oc: str
    fecha: str
    proveedor: str
    insumo: str
    cantidad: int
    monto_total: float
    estado: str = "En Tránsito"  # En Tránsito, Recepcionado

    def to_dict(self):
        return asdict(self)

@dataclass
class Proveedor:
    id: int
    ruc: str
    razon_social: str
    contacto: str
    telefono: str
    rubro: str

    def to_dict(self):
        return asdict(self)

@dataclass
class Usuario:
    usuario: str
    nombre: str
    rol: str  # Recepcionista, Cajero, Estilista, Gerente General
    permisos: str
    activo: bool = True

    def to_dict(self):
        return asdict(self)
