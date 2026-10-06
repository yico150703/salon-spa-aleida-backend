"""
=============================================================================
CAPA 1: CONTROLADORES (CONTROLLER LAYER - REST API)
Mapea las peticiones HTTP hacia los Servicios de Negocio correspondientes
Conforme al Patrón MVC y Sección 3.8.1 del Documento de Arquitectura
=============================================================================
"""

from flask import Blueprint, jsonify, request
from daos.repositories import (
    ClienteDAO, CitaDAO, VentaDAO, CajaDAO,
    ProductoDAO, CompraDAO, ServicioDAO, UsuarioDAO
)
from services.business_services import (
    CitaService, VentaService, CajaService, ReporteService
)

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Inyección de dependencias (DAOs -> Servicios)
cliente_dao = ClienteDAO()
cita_dao = CitaDAO()
venta_dao = VentaDAO()
caja_dao = CajaDAO()
producto_dao = ProductoDAO()
compra_dao = CompraDAO()
servicio_dao = ServicioDAO()
usuario_dao = UsuarioDAO()

cita_service = CitaService(cita_dao, cliente_dao)
venta_service = VentaService(venta_dao, cita_dao, caja_dao)
caja_service = CajaService(caja_dao)
reporte_service = ReporteService(cita_dao, venta_dao, caja_dao)

@api_bp.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "Online",
        "arquitectura": "4 Capas (Presentación -> Control/Negocio -> Acceso a Datos DAO -> Base de Datos)",
        "patron": "MVC + DAO Composite",
        "casos_de_uso": 9,
        "requerimientos_funcionales": 12,
        "objetivos_smart": 4
    })

# INSPECTOR DIDÁCTICO DE ARQUITECTURA
@api_bp.route("/arquitectura/trace", methods=["GET"])
def architecture_trace():
    """Devuelve la explicación didáctica en tiempo real de cómo viaja la petición por las 4 capas."""
    accion = request.args.get("accion", "agendar_cita")
    traces = {
        "agendar_cita": {
            "caso_de_uso": "CU01: Gestionar Citas y Agenda [RF02]",
            "capa_1_presentacion": "React Portal / Formulario de Reserva con selector de terapeuta y fecha",
            "capa_2_controlador": "Flask Controller: POST /api/citas -> cita_service.agendar_cita()",
            "capa_2_regla_negocio": "Validación de no-colisión de horario para el estilista + creación de cliente (RF01)",
            "capa_3_dao": "CitaDAO.save(Cita) y ClienteDAO.save(Cliente)",
            "capa_4_entidad": "Entidades 'Cita' y 'Cliente' almacenadas en base de datos"
        },
        "cobrar_venta": {
            "caso_de_uso": "CU03: Registrar Venta y Cobro [RF04, RF05]",
            "capa_1_presentacion": "React POS Terminal / Selector de medio de pago y botón 'Cobrar'",
            "capa_2_controlador": "Flask Controller: POST /api/ventas -> venta_service.procesar_venta()",
            "capa_2_regla_negocio": "Cálculo de IGV (18%), correlativo B001, cita a Atendida e ingreso a Caja",
            "capa_3_dao": "VentaDAO.save(Venta) y CajaDAO.add_movimiento()",
            "capa_4_entidad": "Entidades 'Venta' y 'Caja' sincronizadas"
        },
        "arqueo_caja": {
            "caso_de_uso": "CU05: Gestionar Operaciones de Caja [RF08]",
            "capa_1_presentacion": "React Calculadora de Arqueo / Conteo físico de billetes y monedas",
            "capa_2_controlador": "Flask Controller: POST /api/caja/cierre -> caja_service.realizar_arqueo_y_cierre()",
            "capa_2_regla_negocio": "Conciliación física vs saldo teórico, cálculo de discrepancia y emisión de Reporte Z",
            "capa_3_dao": "CajaDAO.update_caja() y CajaDAO.get_movimientos()",
            "capa_4_entidad": "Entidad 'Caja' con estado 'Cerrada'"
        }
    }
    return jsonify(traces.get(accion, traces["agendar_cita"]))

# CU01: Citas y Agenda [RF02, RF03]
@api_bp.route("/citas", methods=["GET"])
def get_citas():
    return jsonify(cita_service.listar_citas())

@api_bp.route("/citas", methods=["POST"])
def post_cita():
    data = request.json or {}
    res = cita_service.agendar_cita(data)
    status_code = 201 if res.get("success") else 400
    return jsonify(res), status_code

@api_bp.route("/citas/<int:cita_id>/reprogramar", methods=["PUT"])
def reprogram_cita(cita_id):
    data = request.json or {}
    res = cita_service.reprogramar_cita(cita_id, data.get("nueva_fecha"), data.get("nueva_hora"))
    return jsonify(res), (200 if res.get("success") else 400)

@api_bp.route("/citas/<int:cita_id>/estado", methods=["PUT"])
def change_cita_estado(cita_id):
    data = request.json or {}
    res = cita_service.cambiar_estado(cita_id, data.get("estado"), data.get("motivo"))
    return jsonify(res), (200 if res.get("success") else 400)

# CU02: Gestión de Clientes [RF01]
@api_bp.route("/clientes", methods=["GET"])
def get_clientes():
    return jsonify([c.to_dict() for c in cliente_dao.find_all()])

@api_bp.route("/clientes", methods=["POST"])
def post_cliente():
    data = request.json or {}
    nuevo = Cliente(
        dni=str(data.get("dni", "")),
        nombre=data.get("nombre", ""),
        telefono=data.get("telefono", ""),
        preferencias=data.get("preferencias", "Ficha estética nueva")
    )
    guardado = cliente_dao.save(nuevo)
    return jsonify({"success": True, "cliente": guardado.to_dict()}), 201

# CU03: Ventas y Cobro [RF04, RF05]
@api_bp.route("/ventas", methods=["GET"])
def get_ventas():
    return jsonify(venta_service.listar_ventas())

@api_bp.route("/ventas", methods=["POST"])
def post_venta():
    data = request.json or {}
    res = venta_service.procesar_venta(data)
    return jsonify(res), (201 if res.get("success") else 400)

# CU04: Anulación de Venta [RF06]
@api_bp.route("/anulaciones", methods=["GET"])
def get_anulaciones():
    return jsonify(venta_dao.get_anulaciones())

@api_bp.route("/anulaciones", methods=["POST"])
def post_anulacion():
    data = request.json or {}
    res = venta_service.anular_venta(data)
    return jsonify(res), (201 if res.get("success") else 400)

# CU05: Operaciones de Caja [RF07, RF08]
@api_bp.route("/caja", methods=["GET"])
def get_caja():
    return jsonify(caja_service.obtener_estado_caja())

@api_bp.route("/caja/egreso", methods=["POST"])
def post_egreso():
    data = request.json or {}
    res = caja_service.registrar_egreso(float(data.get("monto", 0.0)), data.get("motivo", "Egreso menor"))
    return jsonify(res), (200 if res.get("success") else 400)

@api_bp.route("/caja/cierre", methods=["POST"])
def post_cierre():
    data = request.json or {}
    conteo_fisico = float(data.get("conteo_fisico", 0.0))
    res = caja_service.realizar_arqueo_y_cierre(conteo_fisico)
    return jsonify(res), 200

# CU06: Compras e Insumos [RF09]
@api_bp.route("/compras", methods=["GET"])
def get_compras():
    return jsonify([p.to_dict() for p in producto_dao.find_all()])

@api_bp.route("/compras/orden", methods=["POST"])
def post_orden_compra():
    data = request.json or {}
    nueva_oc = Compra(
        id=0,
        numero_oc=f"OC-2026-{len(compra_dao.find_all()) + 89:03d}",
        fecha=datetime.now().strftime("%Y-%m-%d"),
        proveedor=data.get("proveedor", "L'Oréal Professionnel"),
        insumo=data.get("insumo", "Tinte Capilar"),
        cantidad=int(data.get("cantidad", 12)),
        monto_total=float(data.get("monto_total", 336.0)),
        estado="Enviada / En Tránsito"
    )
    guardada = compra_dao.save(nueva_oc)
    return jsonify({"success": True, "orden": guardada.to_dict()}), 201

# CU07: Catálogo de Servicios [RF10]
@api_bp.route("/catalogo", methods=["GET"])
def get_catalogo():
    return jsonify([s.to_dict() for s in servicio_dao.find_all()])

# CU08: Usuarios y Roles [RF11]
@api_bp.route("/usuarios", methods=["GET"])
def get_usuarios():
    return jsonify([u.to_dict() for u in usuario_dao.find_all()])

# CU09: Reportes Gerenciales y Metas SMART [RF12]
@api_bp.route("/reportes", methods=["GET"])
def get_reportes():
    return jsonify(reporte_service.obtener_metricas_completas())
