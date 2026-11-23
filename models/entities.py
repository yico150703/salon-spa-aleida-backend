"""
=============================================================================
CAPA 4: BASE DE DATOS Y ENTIDADES DE NEGOCIO (MODELOS OFICIALES CANÓNICOS)
Define las 11 Entidades de Negocio del Sistema de Salon Spa Aleida S.A.C.
Conforme al Diagrama General de Clases de Rational Rose (Modelo Lógico Canónico)
Estructura de 11 clases y atributos 100% idénticos al modelo RUP evaluado.
=============================================================================
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. CLASE: FichaEstetica
# -----------------------------------------------------------------------------
class FichaEstetica:
    def __init__(self, codigficha: str = "", dni_cliente: str = "", tipopiel: str = "Mixta",
                 alergias: str = "Ninguna declarada", tratamientosprevios: str = "",
                 condicionesmedicas: str = "Ninguna",
                 diagnosticoinicial: str = "Apto para tratamientos convencionales",
                 fechacreacion: str = "", **kwargs):
        self.codigficha = codigficha or kwargs.get('codigo_ficha', 'FICH-001')
        self.dni_cliente = dni_cliente
        self.tipopiel = tipopiel or kwargs.get('tipo_piel', 'Mixta')
        self.alergias = alergias
        self.tratamientosprevios = tratamientosprevios or kwargs.get('tratamientos_previos', '')
        self.condicionesmedicas = condicionesmedicas or kwargs.get('condiciones_medicas', 'Ninguna')
        self.diagnosticoinicial = diagnosticoinicial or kwargs.get('diagnostico_inicial', 'Apto para tratamientos convencionales')
        self.fechacreacion = fechacreacion or kwargs.get('fecha_creacion', datetime.now().strftime("%Y-%m-%d"))

    # Propiedades de compatibilidad
    @property
    def CodigFicha(self): return self.codigficha
    @property
    def codigo_ficha(self): return self.codigficha
    @property
    def DNI_Cliente(self): return self.dni_cliente
    @property
    def TipoPiel(self): return self.tipopiel
    @property
    def tipo_piel(self): return self.tipopiel
    @property
    def Alergias(self): return self.alergias
    @property
    def TratamientosPrevios(self): return self.tratamientosprevios
    @property
    def tratamientos_previos(self): return self.tratamientosprevios
    @property
    def CondicionesMedicas(self): return self.condicionesmedicas
    @property
    def condiciones_medicas(self): return self.condicionesmedicas
    @property
    def DiagnosticoInicial(self): return self.diagnosticoinicial
    @property
    def diagnostico_inicial(self): return self.diagnosticoinicial
    @property
    def FechaCreacion(self): return self.fechacreacion
    @property
    def fecha_creacion(self): return self.fechacreacion

    # Métodos del Diagrama de Clases
    def registrarFicha(self) -> bool:
        return bool(self.codigficha and self.dni_cliente)

    def actualizarDiagnostico(self, nuevo_diagnostico: str) -> bool:
        self.diagnosticoinicial = nuevo_diagnostico
        return True

    def consultarAntecedentes(self) -> str:
        return f"Piel: {self.tipopiel} | Alergias: {self.alergias} | Condiciones: {self.condicionesmedicas}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'codigficha': self.codigficha,
            'codigo_ficha': self.codigficha,
            'dni_cliente': self.dni_cliente,
            'tipopiel': self.tipopiel,
            'tipo_piel': self.tipopiel,
            'alergias': self.alergias,
            'tratamientosprevios': self.tratamientosprevios,
            'tratamientos_previos': self.tratamientosprevios,
            'condicionesmedicas': self.condicionesmedicas,
            'condiciones_medicas': self.condicionesmedicas,
            'diagnosticoinicial': self.diagnosticoinicial,
            'diagnostico_inicial': self.diagnosticoinicial,
            'fechacreacion': self.fechacreacion,
            'fecha_creacion': self.fechacreacion
        }


# -----------------------------------------------------------------------------
# 2. CLASE: Cliente
# -----------------------------------------------------------------------------
class Cliente:
    def __init__(self, dni: str = "", nombres: str = "", apellidos: str = "",
                 telefono: str = "", direccion: str = "Lima, Perú",
                 preferencias: str = "", fecharegistro: str = "",
                 estadopadron: str = "Activo", **kwargs):
        self.dni = dni
        self.nombres = nombres or kwargs.get('nombre', '')
        self.apellidos = apellidos
        self.telefono = telefono
        self.direccion = direccion
        self.preferencias = preferencias
        self.fecharegistro = fecharegistro or kwargs.get('fecha_registro', datetime.now().strftime("%Y-%m-%d"))
        self.estadopadron = estadopadron or kwargs.get('estado_padron', 'Activo')
        self.correo = kwargs.get('correo', '')
        self.visitas = kwargs.get('visitas', 1)
        self.ultima_visita = kwargs.get('ultima_visita', datetime.now().strftime("%Y-%m-%d"))

    # Propiedades de compatibilidad
    @property
    def DNI(self): return self.dni
    @property
    def Nombres(self): return self.nombres
    @property
    def nombre(self): return self.nombres
    @nombre.setter
    def nombre(self, val): self.nombres = val
    @property
    def Apellidos(self): return self.apellidos
    @property
    def Telefono(self): return self.telefono
    @property
    def Direccion(self): return self.direccion
    @property
    def Preferencias(self): return self.preferencias
    @property
    def FechaRegistro(self): return self.fecharegistro
    @property
    def fecha_registro(self): return self.fecharegistro
    @property
    def EstadoPadron(self): return self.estadopadron
    @property
    def estado_padron(self): return self.estadopadron

    # Métodos del Diagrama de Clases
    def registrarCliente(self) -> bool:
        return bool(self.dni and self.nombres)

    def actualizarDatos(self, telefono: str, correo: str, preferencias: str) -> bool:
        self.telefono = telefono
        self.correo = correo
        self.preferencias = preferencias
        return True

    def consultarHistorial(self) -> List[dict]:
        return []

    def validarDNI(self) -> bool:
        return len(self.dni) in (8, 11) and self.dni.isdigit()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'dni': self.dni,
            'nombres': self.nombres,
            'nombre': self.nombres,
            'apellidos': self.apellidos,
            'telefono': self.telefono,
            'direccion': self.direccion,
            'preferencias': self.preferencias,
            'fecharegistro': self.fecharegistro,
            'fecha_registro': self.fecharegistro,
            'estadopadron': self.estadopadron,
            'estado_padron': self.estadopadron,
            'correo': self.correo,
            'visitas': self.visitas,
            'ultima_visita': self.ultima_visita
        }


# -----------------------------------------------------------------------------
# 3. CLASE: Cita
# -----------------------------------------------------------------------------
class Cita:
    def __init__(self, codigcita: str = "", codigreserva: str = "", fecha: str = "",
                 horainicio: str = "", horafin: str = "", dni_cliente: str = "",
                 especialista: str = "", montototal: float = 0.0,
                 estado: str = "Confirmada", motivocancelacion: Optional[str] = None,
                 observaciones: str = "", **kwargs):
        self.codigcita = str(codigcita or kwargs.get('id', '1'))
        self.codigreserva = codigreserva or kwargs.get('codigo_reserva', f"RES-{self.codigcita}")
        self.fecha = fecha
        self.horainicio = horainicio or kwargs.get('hora_inicio', kwargs.get('hora', '09:00'))
        self.horafin = horafin or kwargs.get('hora_fin', '10:00')
        self.dni_cliente = dni_cliente or kwargs.get('dni', '')
        self.especialista = especialista
        self.montototal = float(montototal if montototal else kwargs.get('monto', 0.0))
        self.estado = estado
        self.motivocancelacion = motivocancelacion or kwargs.get('motivo_cancelacion')
        self.observaciones = observaciones
        self.cliente = kwargs.get('cliente', '')
        self.servicio = kwargs.get('servicio', '')
        self.cabina = kwargs.get('cabina', 'Cabina Principal')
        self.cobrado = kwargs.get('cobrado', False)

    # Propiedades de compatibilidad
    @property
    def CodigCita(self): return self.codigcita
    @property
    def id(self):
        try: return int(self.codigcita)
        except ValueError: return self.codigcita
    @id.setter
    def id(self, val): self.codigcita = str(val)
    @property
    def CodigReserva(self): return self.codigreserva
    @property
    def Fecha(self): return self.fecha
    @property
    def HoraInicio(self): return self.horainicio
    @property
    def hora(self): return self.horainicio
    @hora.setter
    def hora(self, val): self.horainicio = val
    @property
    def hora_inicio(self): return self.horainicio
    @property
    def HoraFin(self): return self.horafin
    @property
    def hora_fin(self): return self.horafin
    @property
    def DNI_Cliente(self): return self.dni_cliente
    @property
    def dni(self): return self.dni_cliente
    @dni.setter
    def dni(self, val): self.dni_cliente = val
    @property
    def Especialista(self): return self.especialista
    @property
    def MontoTotal(self): return self.montototal
    @property
    def monto(self): return self.montototal
    @monto.setter
    def monto(self, val): self.montototal = float(val)
    @property
    def Estado(self): return self.estado
    @property
    def MotivoCancelacion(self): return self.motivocancelacion
    @MotivoCancelacion.setter
    def MotivoCancelacion(self, val): self.motivocancelacion = val
    @property
    def motivo_cancelacion(self): return self.motivocancelacion
    @motivo_cancelacion.setter
    def motivo_cancelacion(self, val): self.motivocancelacion = val
    @property
    def Observaciones(self): return self.observaciones

    # Métodos del Diagrama de Clases
    def agendarCita(self) -> bool:
        self.estado = "Confirmada"
        return True

    def validarDisponibilidad(self) -> bool:
        return self.estado not in ("Cancelada", "Atendida")

    def reprogramarCita(self, nueva_fecha: str, nueva_hora: str) -> bool:
        self.fecha = nueva_fecha
        self.horainicio = nueva_hora
        self.estado = "Confirmada"
        return True

    def cancelarCita(self, motivo: str) -> bool:
        self.estado = "Cancelada"
        self.motivocancelacion = motivo
        return True

    def marcarTratamientoCulminado(self):
        self.estado = "Atendida"

    def liberarCabina(self) -> bool:
        return True

    def generarTicketConfirmacion(self) -> str:
        return f"CITA-{self.codigcita} | {self.cliente} | {self.fecha} {self.horainicio} | {self.servicio}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'codigcita': self.codigcita,
            'id': self.id,
            'codigreserva': self.codigreserva,
            'codigo_reserva': self.codigreserva,
            'fecha': self.fecha,
            'horainicio': self.horainicio,
            'hora_inicio': self.horainicio,
            'hora': self.horainicio,
            'horafin': self.horafin,
            'hora_fin': self.horafin,
            'dni_cliente': self.dni_cliente,
            'dni': self.dni_cliente,
            'cliente': self.cliente,
            'servicio': self.servicio,
            'especialista': self.especialista,
            'cabina': self.cabina,
            'montototal': self.montototal,
            'monto': self.montototal,
            'estado': self.estado,
            'cobrado': self.cobrado,
            'motivocancelacion': self.motivocancelacion,
            'motivo_cancelacion': self.motivocancelacion,
            'observaciones': self.observaciones
        }


# -----------------------------------------------------------------------------
# 4. CLASE: Servicio
# -----------------------------------------------------------------------------
class Servicio:
    def __init__(self, codigservicio: str = "", nombre: str = "", categoria: str = "",
                 preciobase: float = 0.0, duracionminutos: int = 45,
                 cabinarequerida: str = "Cabina Estándar",
                 porcentajecomision: float = 25.0, estadoactivo: bool = True, **kwargs):
        self.codigservicio = str(codigservicio or kwargs.get('id', '1'))
        self.nombre = nombre
        self.categoria = categoria
        self.preciobase = float(preciobase if preciobase else kwargs.get('precio', 0.0))
        self.duracionminutos = int(duracionminutos if duracionminutos else kwargs.get('duracion', 45))
        self.cabinarequerida = cabinarequerida or kwargs.get('cabina_requerida', 'Cabina Estándar')
        self.porcentajecomision = float(porcentajecomision if porcentajecomision else kwargs.get('comision', 25.0))
        self.estadoactivo = estadoactivo if estadoactivo is not None else kwargs.get('activo', True)

    # Propiedades de compatibilidad
    @property
    def CodigServicio(self): return self.codigservicio
    @property
    def id(self):
        try: return int(self.codigservicio)
        except ValueError: return self.codigservicio
    @id.setter
    def id(self, val): self.codigservicio = str(val)
    @property
    def Nombre(self): return self.nombre
    @property
    def Categoria(self): return self.categoria
    @property
    def PrecioBase(self): return self.preciobase
    @property
    def precio(self): return self.preciobase
    @precio.setter
    def precio(self, val): self.preciobase = float(val)
    @property
    def DuracionMinutos(self): return self.duracionminutos
    @DuracionMinutos.setter
    def DuracionMinutos(self, val): self.duracionminutos = int(val)
    @property
    def duracion(self): return self.duracionminutos
    @duracion.setter
    def duracion(self, val): self.duracionminutos = int(val)
    @property
    def CabinaRequerida(self): return self.cabinarequerida
    @CabinaRequerida.setter
    def CabinaRequerida(self, val): self.cabinarequerida = str(val)
    @property
    def cabina_requerida(self): return self.cabinarequerida
    @cabina_requerida.setter
    def cabina_requerida(self, val): self.cabinarequerida = str(val)
    @property
    def PorcentajeComision(self): return self.porcentajecomision
    @PorcentajeComision.setter
    def PorcentajeComision(self, val): self.porcentajecomision = float(val)
    @property
    def comision(self): return int(self.porcentajecomision)
    @comision.setter
    def comision(self, val): self.porcentajecomision = float(val)
    @property
    def EstadoActivo(self): return self.estadoactivo
    @EstadoActivo.setter
    def EstadoActivo(self, val): self.estadoactivo = bool(val)
    @property
    def activo(self): return self.estadoactivo
    @activo.setter
    def activo(self, val): self.estadoactivo = bool(val)

    # Métodos del Diagrama de Clases
    def registrarServicio(self) -> bool:
        return bool(self.nombre and self.preciobase > 0)

    def actualizarTarifa(self, nuevo_precio: float) -> bool:
        if nuevo_precio > 0:
            self.preciobase = nuevo_precio
            return True
        return False

    def asignarComision(self, porcentaje: int) -> bool:
        if 0 <= porcentaje <= 100:
            self.porcentajecomision = float(porcentaje)
            return True
        return False

    def inactivarServicio(self) -> bool:
        self.estadoactivo = False
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            'codigservicio': self.codigservicio,
            'id': self.id,
            'nombre': self.nombre,
            'categoria': self.categoria,
            'preciobase': self.preciobase,
            'precio': self.preciobase,
            'duracionminutos': self.duracionminutos,
            'duracion': self.duracionminutos,
            'cabinarequerida': self.cabinarequerida,
            'porcentajecomision': self.porcentajecomision,
            'comision': self.comision,
            'estadoactivo': self.estadoactivo,
            'activo': self.estadoactivo
        }


# -----------------------------------------------------------------------------
# 5. CLASE: Usuario
# -----------------------------------------------------------------------------
class Usuario:
    def __init__(self, username: str = "", codigusuario: str = "", passwordhash: str = "",
                 nombres: str = "", apellidos: str = "", dni: Optional[str] = None,
                 rol: str = "Recepcionista", turno: str = "Turno Completo",
                 celular: Optional[str] = None, email: Optional[str] = None,
                 estado: bool = True, **kwargs):
        self.username = username or kwargs.get('usuario', '')
        self.codigusuario = codigusuario or kwargs.get('cod_usuario', 'USR-001')
        self.passwordhash = passwordhash or kwargs.get('password_hash', 'pbkdf2:sha256:260000$default')
        self.nombres = nombres or kwargs.get('nombre', '')
        self.apellidos = apellidos
        self.dni = dni
        self.rol = rol
        self.turno = turno
        self.celular = celular or kwargs.get('telefono')
        self.email = email
        self.estado = estado if estado is not None else kwargs.get('activo', True)
        self.permisos = kwargs.get('permisos', '')
        self._password_temporal = kwargs.get('password_temporal', '')

    @property
    def password_temporal(self): return getattr(self, '_password_temporal', '')
    @password_temporal.setter
    def password_temporal(self, val): self._password_temporal = val

    # Propiedades de compatibilidad
    @property
    def Username(self): return self.username
    @property
    def usuario(self): return self.username
    @property
    def CodigUsuario(self): return self.codigusuario
    @property
    def cod_usuario(self): return self.codigusuario
    @cod_usuario.setter
    def cod_usuario(self, val): self.codigusuario = val
    @property
    def PasswordHash(self): return self.passwordhash
    @property
    def password_hash(self): return self.passwordhash
    @property
    def Nombres(self): return self.nombres
    @property
    def nombre(self): return self.nombres
    @property
    def Apellidos(self): return self.apellidos
    @property
    def DNI(self): return self.dni
    @property
    def Rol(self): return self.rol
    @property
    def Turno(self): return self.turno
    @property
    def Celular(self): return self.celular
    @property
    def telefono(self): return self.celular
    @property
    def Email(self): return self.email
    @property
    def Estado(self): return self.estado
    @property
    def activo(self): return self.estado

    # Métodos del Diagrama de Clases
    def autenticar(self, password: str) -> bool:
        return bool(self.estado and password)

    def cambiarPassword(self, nueva_clave: str) -> bool:
        return len(nueva_clave) >= 6

    def asignarRol(self, nuevo_rol: str) -> bool:
        self.rol = nuevo_rol
        return True

    def validarPermiso(self, modulo: str) -> bool:
        return bool(modulo.lower() in self.permisos.lower() or self.rol == "Administrador")

    def to_dict(self) -> Dict[str, Any]:
        return {
            'username': self.username,
            'usuario': self.username,
            'codigusuario': self.codigusuario,
            'cod_usuario': self.codigusuario,
            'nombres': self.nombres,
            'nombre': self.nombres,
            'apellidos': self.apellidos,
            'dni': self.dni,
            'rol': self.rol,
            'turno': self.turno,
            'celular': self.celular,
            'telefono': self.celular,
            'email': self.email,
            'estado': self.estado,
            'activo': self.estado,
            'permisos': self.permisos
        }


# -----------------------------------------------------------------------------
# 6. CLASE: VentaComprobante (Alias canónico: Venta)
# -----------------------------------------------------------------------------
class VentaComprobante:
    def __init__(self, numerocomprobante: str = "", tipocomprobante: str = "Boleta de Venta",
                 serie: str = "B001", fechaemision: str = "", horaemision: str = "",
                 dni_cliente: str = "", subtotal: float = 0.0, igv: float = 0.0,
                 descuentototal: float = 0.0, totalneto: float = 0.0,
                 estadocomprobante: str = "Emitida", notacredito: Optional[str] = None, **kwargs):
        self.numerocomprobante = numerocomprobante or kwargs.get('numero_boleta', 'B001-000001')
        self.tipocomprobante = tipocomprobante or kwargs.get('tipo_comprobante', 'Boleta de Venta')
        self.serie = serie
        self.fechaemision = fechaemision or kwargs.get('fecha', datetime.now().strftime("%Y-%m-%d"))
        self.horaemision = horaemision or kwargs.get('hora_emision', datetime.now().strftime("%H:%M"))
        self.dni_cliente = dni_cliente
        self.subtotal = float(subtotal if subtotal else kwargs.get('subtotal', 0.0))
        self.igv = float(igv if igv else kwargs.get('igv', 0.0))
        self.descuentototal = float(descuentototal if descuentototal else kwargs.get('descuento', 0.0))
        self.totalneto = float(totalneto if totalneto else kwargs.get('total', 0.0))
        self.estadocomprobante = estadocomprobante or kwargs.get('estado', 'Emitida')
        self.notacredito = notacredito or kwargs.get('nota_credito')
        self.id = kwargs.get('id', 1)
        self.cliente = kwargs.get('cliente', '')
        self.servicio = kwargs.get('servicio', '')
        self.medio_pago = kwargs.get('medio_pago', 'Efectivo')

    # Propiedades de compatibilidad
    @property
    def NumeroComprobante(self): return self.numerocomprobante
    @property
    def numero_boleta(self): return self.numerocomprobante
    @numero_boleta.setter
    def numero_boleta(self, val): self.numerocomprobante = val
    @property
    def TipoComprobante(self): return self.tipocomprobante
    @property
    def tipo_comprobante(self): return self.tipocomprobante
    @property
    def Serie(self): return self.serie
    @property
    def FechaEmision(self): return self.fechaemision
    @property
    def fecha(self): return self.fechaemision
    @property
    def HoraEmision(self): return self.horaemision
    @property
    def hora_emision(self): return self.horaemision
    @property
    def DNI_Cliente(self): return self.dni_cliente
    @property
    def Subtotal(self): return self.subtotal
    @property
    def IGV(self): return self.igv
    @property
    def DescuentoTotal(self): return self.descuentototal
    @property
    def descuento(self): return self.descuentototal
    @property
    def TotalNeto(self): return self.totalneto
    @property
    def total(self): return self.totalneto
    @total.setter
    def total(self, val): self.totalneto = float(val)
    @property
    def EstadoComprobante(self): return self.estadocomprobante
    @property
    def estado(self): return self.estadocomprobante
    @property
    def nota_credito(self): return self.notacredito

    # Métodos del Diagrama de Clases
    def registrarVenta(self) -> bool:
        self.estadocomprobante = "Emitida"
        return True

    def calcularSubtotal(self) -> float:
        return round(self.totalneto / 1.18, 2)

    def calcularIGV(self) -> float:
        return round(self.totalneto - self.calcularSubtotal(), 2)

    def aplicarDescuento(self, monto_desc: float) -> float:
        self.descuentototal = monto_desc
        self.totalneto = max(0.0, self.totalneto - monto_desc)
        return self.totalneto

    def anularVenta(self, motivo: str, pin_autorizacion: str = "1234") -> bool:
        if pin_autorizacion == "1234":
            self.estadocomprobante = "Anulada"
            return True
        return False

    def emitirNotaCredito(self) -> str:
        if not self.notacredito:
            self.notacredito = f"NC-{datetime.now().strftime('%Y%m%d%H%M')}"
        return self.notacredito

    def to_dict(self) -> Dict[str, Any]:
        return {
            'numerocomprobante': self.numerocomprobante,
            'numero_boleta': self.numerocomprobante,
            'id': self.id,
            'tipocomprobante': self.tipocomprobante,
            'tipo_comprobante': self.tipocomprobante,
            'serie': self.serie,
            'fechaemision': self.fechaemision,
            'fecha': self.fechaemision,
            'horaemision': self.horaemision,
            'hora_emision': self.horaemision,
            'dni_cliente': self.dni_cliente,
            'cliente': self.cliente,
            'servicio': self.servicio,
            'subtotal': self.subtotal,
            'igv': self.igv,
            'descuentototal': self.descuentototal,
            'descuento': self.descuentototal,
            'totalneto': self.totalneto,
            'total': self.totalneto,
            'medio_pago': self.medio_pago,
            'estadocomprobante': self.estadocomprobante,
            'estado': self.estadocomprobante,
            'notacredito': self.notacredito,
            'nota_credito': self.notacredito
        }

# Alias para máxima compatibilidad
Venta = VentaComprobante


# -----------------------------------------------------------------------------
# 7. CLASE: DetalleComprobante
# -----------------------------------------------------------------------------
class DetalleComprobante:
    def __init__(self, item: int = 1, numerocomprobante: str = "", codigitem: str = "",
                 tipoitem: str = "Servicio", descripcion: str = "", cantidad: int = 1,
                 preciounitario: float = 0.0, subtotal: float = 0.0, **kwargs):
        self.item = int(item)
        self.numerocomprobante = numerocomprobante or kwargs.get('numero_comprobante', '')
        self.codigitem = codigitem or kwargs.get('codigo_item', '')
        self.tipoitem = tipoitem or kwargs.get('tipo_item', 'Servicio')
        self.descripcion = descripcion
        self.cantidad = int(cantidad)
        self.preciounitario = float(preciounitario if preciounitario else kwargs.get('precio_unitario', 0.0))
        self.subtotal = float(subtotal if subtotal else round(self.cantidad * self.preciounitario, 2))

    # Propiedades de compatibilidad
    @property
    def Item(self): return self.item
    @property
    def NumeroComprobante(self): return self.numerocomprobante
    @property
    def numero_comprobante(self): return self.numerocomprobante
    @property
    def CodigItem(self): return self.codigitem
    @property
    def codigo_item(self): return self.codigitem
    @property
    def TipoItem(self): return self.tipoitem
    @property
    def tipo_item(self): return self.tipoitem
    @property
    def Descripcion(self): return self.descripcion
    @property
    def Cantidad(self): return self.cantidad
    @property
    def PrecioUnitario(self): return self.preciounitario
    @property
    def precio_unitario(self): return self.preciounitario
    @property
    def Subtotal(self): return self.subtotal

    # Métodos del Diagrama de Clases
    def agregarItem(self) -> bool:
        self.subtotal = round(self.cantidad * self.preciounitario, 2)
        return True

    def calcularImporte(self) -> float:
        self.subtotal = round(self.cantidad * self.preciounitario, 2)
        return self.subtotal

    def eliminarItem(self) -> bool:
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            'item': self.item,
            'numerocomprobante': self.numerocomprobante,
            'numero_comprobante': self.numerocomprobante,
            'codigitem': self.codigitem,
            'codigo_item': self.codigitem,
            'tipoitem': self.tipoitem,
            'tipo_item': self.tipoitem,
            'descripcion': self.descripcion,
            'cantidad': self.cantidad,
            'preciounitario': self.preciounitario,
            'precio_unitario': self.preciounitario,
            'subtotal': self.subtotal
        }


# -----------------------------------------------------------------------------
# 8. CLASE: Promocion
# -----------------------------------------------------------------------------
class Promocion:
    def __init__(self, codigpromocion: str = "", nombre: str = "",
                 porcentajedescuento: float = 0.0, montodescuento: float = 0.0,
                 fechainicio: str = "", fechafin: str = "",
                 condiciones: str = "Válido para pagos en efectivo o billetera digital",
                 estado: str = "Vigente", **kwargs):
        self.codigpromocion = codigpromocion or kwargs.get('codigo_promocion', 'PROM-001')
        self.nombre = nombre
        self.porcentajedescuento = float(porcentajedescuento if porcentajedescuento else kwargs.get('porcentaje_descuento', 0.0))
        self.montodescuento = float(montodescuento if montodescuento else kwargs.get('monto_descuento', 0.0))
        self.fechainicio = fechainicio or kwargs.get('fecha_inicio', datetime.now().strftime("%Y-%m-%d"))
        self.fechafin = fechafin or kwargs.get('fecha_fin', '')
        self.condiciones = condiciones
        self.estado = estado

    # Propiedades de compatibilidad
    @property
    def CodigPromocion(self): return self.codigpromocion
    @property
    def codigo_promocion(self): return self.codigpromocion
    @property
    def Nombre(self): return self.nombre
    @property
    def PorcentajeDescuento(self): return self.porcentajedescuento
    @property
    def porcentaje_descuento(self): return self.porcentajedescuento
    @property
    def MontoDescuento(self): return self.montodescuento
    @property
    def monto_descuento(self): return self.montodescuento
    @property
    def FechaInicio(self): return self.fechainicio
    @property
    def fecha_inicio(self): return self.fechainicio
    @property
    def FechaFin(self): return self.fechafin
    @property
    def fecha_fin(self): return self.fechafin
    @property
    def Condiciones(self): return self.condiciones
    @property
    def Estado(self): return self.estado

    # Métodos del Diagrama de Clases
    def crearPromocion(self) -> bool:
        return bool(self.codigpromocion and self.nombre)

    def validarVigencia(self) -> bool:
        return self.estado == "Vigente"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'codigpromocion': self.codigpromocion,
            'codigo_promocion': self.codigpromocion,
            'nombre': self.nombre,
            'porcentajedescuento': self.porcentajedescuento,
            'porcentaje_descuento': self.porcentajedescuento,
            'montodescuento': self.montodescuento,
            'monto_descuento': self.montodescuento,
            'fechainicio': self.fechainicio,
            'fecha_inicio': self.fechainicio,
            'fechafin': self.fechafin,
            'fecha_fin': self.fechafin,
            'condiciones': self.condiciones,
            'estado': self.estado
        }


# -----------------------------------------------------------------------------
# 9. CLASE: CajaSesion (Alias canónico: Caja)
# -----------------------------------------------------------------------------
class CajaSesion:
    def __init__(self, codigsesion: str = "", cajero: str = "Cajero General",
                 turno: str = "Turno Mañana", montoapertura: float = 0.0,
                 fechahoraapertura: str = "", montocierresistema: Optional[float] = None,
                 montocierrereal: Optional[float] = None, diferencia: Optional[float] = None,
                 estadosesion: Optional[str] = None, **kwargs):
        self.codigsesion = codigsesion or kwargs.get('codigo_sesion', 'SES-001')
        self.cajero = cajero
        self.turno = turno
        self.montoapertura = float(montoapertura if montoapertura else kwargs.get('apertura', 0.0))
        self.fechahoraapertura = fechahoraapertura or kwargs.get('fecha_hora_apertura', datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.montocierresistema = montocierresistema if montocierresistema is not None else kwargs.get('saldo_teorico', self.montoapertura)
        self.montocierrereal = montocierrereal or kwargs.get('monto_cierre_real')
        self.diferencia = diferencia if diferencia is not None else kwargs.get('diferencia', 0.0)
        self.estadosesion = estadosesion if estadosesion is not None else kwargs.get('estado', 'Abierta')
        self.id = kwargs.get('id', 1)
        self.fecha = kwargs.get('fecha', datetime.now().strftime("%Y-%m-%d"))
        self.efectivo = kwargs.get('efectivo', 0.0)
        self.digital = kwargs.get('digital', 0.0)
        self.egresos = kwargs.get('egresos', 0.0)

    # Propiedades de compatibilidad
    @property
    def CodigSesion(self): return self.codigsesion
    @property
    def codigo_sesion(self): return self.codigsesion
    @property
    def Cajero(self): return self.cajero
    @property
    def Turno(self): return self.turno
    @property
    def MontoApertura(self): return self.montoapertura
    @property
    def apertura(self): return self.montoapertura
    @apertura.setter
    def apertura(self, val): self.montoapertura = float(val)
    @property
    def FechaHoraApertura(self): return self.fechahoraapertura
    @property
    def fecha_hora_apertura(self): return self.fechahoraapertura
    @property
    def MontoCierreSistema(self): return self.montocierresistema
    @property
    def saldo_teorico(self): return self.montocierresistema
    @saldo_teorico.setter
    def saldo_teorico(self, val): self.montocierresistema = float(val)
    @property
    def MontoCierreReal(self): return self.montocierrereal
    @MontoCierreReal.setter
    def MontoCierreReal(self, val): self.montocierrereal = float(val) if val is not None else None

    @property
    def arqueo_fisico(self): return self.montocierrereal
    @arqueo_fisico.setter
    def arqueo_fisico(self, val): self.montocierrereal = float(val) if val is not None else None

    @property
    def total_teorico(self): return self.montocierresistema
    @total_teorico.setter
    def total_teorico(self, val): self.montocierresistema = float(val) if val is not None else 0.0

    @property
    def EstadoSesion(self): return self.estadosesion
    @EstadoSesion.setter
    def EstadoSesion(self, val): self.estadosesion = val

    @property
    def estado(self): return self.estadosesion
    @estado.setter
    def estado(self, val): self.estadosesion = val

    # Métodos del Diagrama de Clases
    def aperturarCaja(self, monto_inicial: float, turno: str) -> bool:
        self.montoapertura = float(monto_inicial)
        self.montocierresistema = float(monto_inicial)
        self.turno = turno
        self.estadosesion = "Abierta"
        return True

    def registrarMovimiento(self, tipo: str, monto: float) -> float:
        if self.montocierresistema is None:
            self.montocierresistema = self.montoapertura
        if tipo.lower() in ("ingreso", "cobro"):
            self.montocierresistema += monto
        else:
            self.egresos += monto
            self.montocierresistema -= monto
        return self.montocierresistema

    def realizarArqueo(self, monto_fisico: float) -> float:
        self.montocierrereal = monto_fisico
        sistema = self.montocierresistema if self.montocierresistema is not None else self.montoapertura
        self.diferencia = round(monto_fisico - sistema, 2)
        return self.diferencia

    def conciliarDiferencia(self) -> bool:
        return self.diferencia == 0.0

    def cerrarCaja(self) -> bool:
        self.estadosesion = "Cerrada"
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            'codigsesion': self.codigsesion,
            'codigo_sesion': self.codigsesion,
            'id': self.id,
            'cajero': self.cajero,
            'turno': self.turno,
            'montoapertura': self.montoapertura,
            'apertura': self.montoapertura,
            'fechahoraapertura': self.fechahoraapertura,
            'fecha_hora_apertura': self.fechahoraapertura,
            'montocierresistema': self.montocierresistema,
            'saldo_teorico': self.montocierresistema,
            'montocierrereal': self.montocierrereal,
            'diferencia': self.diferencia,
            'estadosesion': self.estadosesion,
            'estado': self.estadosesion,
            'fecha': self.fecha,
            'efectivo': self.efectivo,
            'digital': self.digital,
            'egresos': self.egresos
        }

# Alias canónico
Caja = CajaSesion


# -----------------------------------------------------------------------------
# 10. CLASE: Pago
# -----------------------------------------------------------------------------
class Pago:
    def __init__(self, codigpago: str = "", numerocomprobante: str = "", monto: float = 0.0,
                 mediopago: str = "Efectivo", referenciaoperacion: str = "REF-0000",
                 fechahora: str = "", estado: str = "Aprobado", **kwargs):
        self.codigpago = codigpago or kwargs.get('codigo_pago', 'PAG-001')
        self.numerocomprobante = numerocomprobante or kwargs.get('numero_comprobante', '')
        self.monto = float(monto)
        self.mediopago = mediopago or kwargs.get('medio_pago', 'Efectivo')
        self.referenciaoperacion = referenciaoperacion or kwargs.get('referencia_operacion', 'REF-0000')
        self.fechahora = fechahora or kwargs.get('fecha_hora', datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.estado = estado

    # Propiedades de compatibilidad
    @property
    def CodigPago(self): return self.codigpago
    @property
    def codigo_pago(self): return self.codigpago
    @property
    def NumeroComprobante(self): return self.numerocomprobante
    @property
    def numero_comprobante(self): return self.numerocomprobante
    @property
    def Monto(self): return self.monto
    @property
    def MedioPago(self): return self.mediopago
    @property
    def medio_pago(self): return self.mediopago
    @property
    def ReferenciaOperacion(self): return self.referenciaoperacion
    @property
    def referencia_operacion(self): return self.referenciaoperacion
    @property
    def FechaHora(self): return self.fechahora
    @property
    def fecha_hora(self): return self.fechahora
    @property
    def Estado(self): return self.estado

    # Métodos del Diagrama de Clases
    def procesarPago(self) -> bool:
        return self.monto > 0

    def calcularVuelto(self, monto_recibido: float) -> float:
        return max(0.0, round(monto_recibido - self.monto, 2))

    def validarTransaccion(self) -> bool:
        return self.estado == "Aprobado"

    def emitirVoucher(self) -> str:
        return f"PAGO-{self.codigpago} | {self.mediopago} | S/ {self.monto:.2f}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'codigpago': self.codigpago,
            'codigo_pago': self.codigpago,
            'numerocomprobante': self.numerocomprobante,
            'numero_comprobante': self.numerocomprobante,
            'monto': self.monto,
            'mediopago': self.mediopago,
            'medio_pago': self.mediopago,
            'referenciaoperacion': self.referenciaoperacion,
            'referencia_operacion': self.referenciaoperacion,
            'fechahora': self.fechahora,
            'fecha_hora': self.fechahora,
            'estado': self.estado
        }


# -----------------------------------------------------------------------------
# 11. CLASE: MovimientoCaja
# -----------------------------------------------------------------------------
class MovimientoCaja:
    def __init__(self, codigmovimiento: str = "", codigsesion: str = "SES-001",
                 tipomovimiento: str = "Ingreso", concepto: str = "",
                 monto: float = 0.0, fechahora: str = "", autorizadopor: str = "Administración", **kwargs):
        self.codigmovimiento = codigmovimiento or kwargs.get('codigo_movimiento', 'MOV-001')
        self.codigsesion = codigsesion or kwargs.get('codigo_sesion', 'SES-001')
        self.tipomovimiento = tipomovimiento or kwargs.get('tipo_movimiento', kwargs.get('tipo', 'Ingreso'))
        self.concepto = concepto or kwargs.get('detalle', '')
        self.monto = float(monto)
        self.fechahora = fechahora or kwargs.get('fecha_hora', kwargs.get('hora', datetime.now().strftime("%Y-%m-%d %H:%M")))
        self.autorizadopor = autorizadopor or kwargs.get('autorizado_por', 'Administración')
        self.id = kwargs.get('id', 1)

    # Propiedades de compatibilidad
    @property
    def CodigMovimiento(self): return self.codigmovimiento
    @property
    def codigo_movimiento(self): return self.codigmovimiento
    @property
    def CodigSesion(self): return self.codigsesion
    @property
    def codigo_sesion(self): return self.codigsesion
    @property
    def TipoMovimiento(self): return self.tipomovimiento
    @property
    def tipo(self): return self.tipomovimiento
    @property
    def tipo_movimiento(self): return self.tipomovimiento
    @property
    def Concepto(self): return self.concepto
    @property
    def detalle(self): return self.concepto
    @property
    def Monto(self): return self.monto
    @property
    def FechaHora(self): return self.fechahora
    @property
    def fecha_hora(self): return self.fechahora
    @property
    def hora(self): return self.fechahora
    @property
    def AutorizadoPor(self): return self.autorizadopor
    @property
    def autorizado_por(self): return self.autorizadopor

    # Métodos del Diagrama de Clases
    def registrarIngreso(self) -> bool:
        self.tipomovimiento = "Ingreso"
        return self.monto > 0

    def registrarEgreso(self) -> bool:
        self.tipomovimiento = "Egreso"
        return self.monto > 0

    def validarComprobante(self) -> bool:
        return bool(self.concepto and self.monto != 0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'codigmovimiento': self.codigmovimiento,
            'codigo_movimiento': self.codigmovimiento,
            'codigsesion': self.codigsesion,
            'codigo_sesion': self.codigsesion,
            'tipomovimiento': self.tipomovimiento,
            'tipo': self.tipomovimiento,
            'tipo_movimiento': self.tipomovimiento,
            'concepto': self.concepto,
            'detalle': self.concepto,
            'monto': self.monto,
            'fechahora': self.fechahora,
            'fecha_hora': self.fechahora,
            'hora': self.fechahora,
            'autorizadopor': self.autorizadopor,
            'autorizado_por': self.autorizadopor,
            'id': self.id
        }


# -----------------------------------------------------------------------------
# MODELOS AUXILIARES DE SOPORTE LOGÍSTICO Y OPERATIVO
# -----------------------------------------------------------------------------
class Producto:
    def __init__(self, id: int, nombre: str, proveedor: str, stock: int,
                 stock_min: int, costo: float, precio_venta: float, alerta: bool = False):
        self.id = id
        self.nombre = nombre
        self.proveedor = proveedor
        self.stock = stock
        self.stock_min = stock_min
        self.costo = costo
        self.precio_venta = precio_venta
        self.alerta = alerta

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'proveedor': self.proveedor,
            'stock': self.stock,
            'stock_min': self.stock_min,
            'costo': self.costo,
            'precio_venta': self.precio_venta,
            'alerta': self.alerta
        }

class Compra:
    def __init__(self, id: int, numero_oc: str, fecha: str, proveedor: str,
                 insumo: str, cantidad: int, monto_total: float, estado: str = "En Tránsito"):
        self.id = id
        self.numero_oc = numero_oc
        self.fecha = fecha
        self.proveedor = proveedor
        self.insumo = insumo
        self.cantidad = cantidad
        self.monto_total = monto_total
        self.estado = estado

    def to_dict(self):
        return {
            'id': self.id,
            'numero_oc': self.numero_oc,
            'fecha': self.fecha,
            'proveedor': self.proveedor,
            'insumo': self.insumo,
            'cantidad': self.cantidad,
            'monto_total': self.monto_total,
            'estado': self.estado
        }

class Proveedor:
    def __init__(self, id: int, ruc: str, razon_social: str, contacto: str,
                 telefono: str, rubro: str):
        self.id = id
        self.ruc = ruc
        self.razon_social = razon_social
        self.contacto = contacto
        self.telefono = telefono
        self.rubro = rubro

    def to_dict(self):
        return {
            'id': self.id,
            'ruc': self.ruc,
            'razon_social': self.razon_social,
            'contacto': self.contacto,
            'telefono': self.telefono,
            'rubro': self.rubro
        }
