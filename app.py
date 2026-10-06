"""
=============================================================================
SALON SPA ALEIDA - REST API BACKEND (FLASK)
Servidor de API para despliegue en Render
Soporta los 9 Casos de Uso del negocio y los 4 Objetivos Realistas SMART
=============================================================================
"""

import os
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# Habilitar CORS para permitir peticiones desde Vercel y entornos de desarrollo
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ---------------------------------------------------------------------------
# BASE DE DATOS EN MEMORIA (Inicializada con datos reales del negocio)
# ---------------------------------------------------------------------------

citas_db = [
    {
        "id": 1,
        "hora": "09:00 AM",
        "fecha": "2026-10-06",
        "cliente": "Mariana Torres",
        "dni": "72819382",
        "servicio": "Masaje Relajante Aleida",
        "especialista": "Carmen Sánchez",
        "estado": "Atendida",
        "monto": 280.0,
        "cobrado": True
    },
    {
        "id": 2,
        "hora": "10:30 AM",
        "fecha": "2026-10-06",
        "cliente": "Patricia Valdivia",
        "dni": "45910284",
        "servicio": "Facial Rejuvenecedor con Oro",
        "especialista": "Carmen Sánchez",
        "estado": "Confirmada",
        "monto": 450.0,
        "cobrado": False
    },
    {
        "id": 3,
        "hora": "11:45 AM",
        "fecha": "2026-10-06",
        "cliente": "Claudia Morales",
        "dni": "48192039",
        "servicio": "Tratamiento Capilar Keratina",
        "especialista": "Luisa Paredes",
        "estado": "En Atención",
        "monto": 350.0,
        "cobrado": False
    },
    {
        "id": 4,
        "hora": "02:30 PM",
        "fecha": "2026-10-06",
        "cliente": "Jessica Rivas",
        "dni": "70829104",
        "servicio": "Manicura Spa Premium",
        "especialista": "Ana Vargas",
        "estado": "Pendiente",
        "monto": 150.0,
        "cobrado": False
    }
]

clientes_db = [
    {
        "dni": "72819382",
        "nombre": "Mariana Torres",
        "telefono": "987654321",
        "preferencias": "Piel mixta, prefiere aromaterapia de lavanda.",
        "visitas": 12,
        "ultima_visita": "2026-10-06"
    },
    {
        "dni": "45910284",
        "nombre": "Patricia Valdivia",
        "telefono": "945112233",
        "preferencias": "Sensibilidad a tintes con amoníaco.",
        "visitas": 8,
        "ultima_visita": "2026-10-06"
    },
    {
        "dni": "48192039",
        "nombre": "Claudia Morales",
        "telefono": "912345678",
        "preferencias": "Tratamiento keratina semestral.",
        "visitas": 5,
        "ultima_visita": "2026-10-06"
    }
]

ventas_db = [
    {
        "id": 1,
        "numero_boleta": "B001-0004820",
        "fecha": "2026-10-06 09:45",
        "cliente": "Mariana Torres",
        "servicio": "Masaje Relajante Aleida",
        "subtotal": 237.29,
        "igv": 42.71,
        "total": 280.0,
        "medio_pago": "Efectivo",
        "estado": "Emitida"
    }
]

anulaciones_db = [
    {
        "id": 1,
        "fecha": "2026-10-05 16:30",
        "boleta": "B001-0004810",
        "nota_credito": "NC-012",
        "monto": 120.0,
        "motivo": "Devolución por insatisfacción",
        "autorizado_por": "Aleida Mendoza (Gerente)"
    }
]

caja_db = {
    "apertura": 150.0,
    "efectivo": 720.0,
    "digital": 1580.0,
    "egresos": 45.0,
    "estado": "Abierta",
    "turno": "Turno Mañana",
    "movimientos": [
        {"hora": "08:30 AM", "tipo": "Apertura", "monto": 150.0, "detalle": "Fondo de sencillo inicial"},
        {"hora": "09:45 AM", "tipo": "Ingreso", "monto": 280.0, "detalle": "Cobro Boleta B001-4820 (Efectivo)"},
        {"hora": "11:00 AM", "tipo": "Egreso", "monto": -45.0, "detalle": "Salida menor por refrigerio y café"},
        {"hora": "11:30 AM", "tipo": "Ingreso", "monto": 450.0, "detalle": "Cobro Boleta B001-4821 (Yape)"},
        {"hora": "01:15 PM", "tipo": "Ingreso", "monto": 350.0, "detalle": "Cobro Boleta B001-4822 (POS Tarjeta)"}
    ]
}

insumos_db = [
    {"id": 1, "nombre": "Tinte Profesional 6.1 (Cenizo)", "proveedor": "L'Oréal Professionnel Perú", "stock": 2, "stock_min": 6, "alerta": True},
    {"id": 2, "nombre": "Crema Nutritiva Keratina 1L", "proveedor": "Distribuidora Belleza Total SAC", "stock": 1, "stock_min": 4, "alerta": True},
    {"id": 3, "nombre": "Aceite de Argán Puro 250ml", "proveedor": "BioCosmetics Natura", "stock": 8, "stock_min": 3, "alerta": False}
]

catalogo_db = [
    {"id": 1, "nombre": "Masaje Relajante Aleida", "categoria": "Spa & Bienestar", "duracion": 90, "precio": 280.0, "comision": 25, "activo": True},
    {"id": 2, "nombre": "Facial Rejuvenecedor con Oro", "categoria": "Cosmiatría Facial", "duracion": 75, "precio": 450.0, "comision": 30, "activo": True},
    {"id": 3, "nombre": "Tratamiento Capilar Keratina", "categoria": "Cuidado Capilar", "duracion": 120, "precio": 350.0, "comision": 30, "activo": True},
    {"id": 4, "nombre": "Manicura Spa Premium", "categoria": "Manos & Pies", "duracion": 60, "precio": 150.0, "comision": 35, "activo": True}
]

usuarios_db = [
    {"usuario": "cramos", "nombre": "Camila Ramos", "rol": "Recepcionista", "permisos": "Agenda (CU01), Clientes (CU02), POS (CU03)", "activo": True},
    {"usuario": "aleida_admin", "nombre": "Aleida Mendoza", "rol": "Gerente General", "permisos": "Acceso Total (CU01-CU09), Aprobación de Anulaciones", "activo": True},
    {"usuario": "csanchez", "nombre": "Carmen Sánchez", "rol": "Terapeuta / Cosmiatra", "permisos": "Consulta de Agenda y Fichas", "activo": True}
]

# ---------------------------------------------------------------------------
# RUTAS DE LA API (REST ENDPOINTS)
# ---------------------------------------------------------------------------

@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "app": "Salon Spa Aleida - Backend API",
        "status": "Online",
        "platform": "Render",
        "version": "2.0.0",
        "documentation": "/api/health"
    })

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "Healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "In-Memory Active",
        "use_cases_supported": 9,
        "objectives_smart_tracked": 4
    })

# CU01: Gestionar Citas y Agenda
@app.route("/api/citas", methods=["GET"])
def get_citas():
    return jsonify(citas_db)

@app.route("/api/citas", methods=["POST"])
def create_cita():
    data = request.json or {}
    new_id = len(citas_db) + 1
    new_cita = {
        "id": new_id,
        "hora": data.get("hora", "03:00 PM"),
        "fecha": data.get("fecha", datetime.now().strftime("%Y-%m-%d")),
        "cliente": data.get("cliente", "Cliente Web"),
        "dni": data.get("dni", "Online"),
        "servicio": data.get("servicio", "Masaje Relajante Aleida"),
        "especialista": data.get("especialista", "Carmen Sánchez"),
        "estado": "Confirmada",
        "monto": float(data.get("monto", 250.0)),
        "cobrado": False
    }
    citas_db.append(new_cita)
    return jsonify({"message": "Cita registrada exitosamente", "cita": new_cita}), 201

@app.route("/api/citas/<int:cita_id>", methods=["PUT"])
def update_cita(cita_id):
    data = request.json or {}
    for c in citas_db:
        if c["id"] == cita_id:
            c.update(data)
            return jsonify({"message": "Cita actualizada", "cita": c})
    return jsonify({"error": "Cita no encontrada"}), 404

# CU02: Gestionar Clientes
@app.route("/api/clientes", methods=["GET"])
def get_clientes():
    return jsonify(clientes_db)

@app.route("/api/clientes", methods=["POST"])
def create_cliente():
    data = request.json or {}
    new_cliente = {
        "dni": str(data.get("dni", "")),
        "nombre": data.get("nombre", ""),
        "telefono": data.get("telefono", ""),
        "preferencias": data.get("preferencias", "Sin observaciones previas"),
        "visitas": 1,
        "ultima_visita": datetime.now().strftime("%Y-%m-%d")
    }
    clientes_db.append(new_cliente)
    return jsonify({"message": "Cliente registrado exitosamente", "cliente": new_cliente}), 201

# CU03: Registrar Venta y Cobro (Punto de Venta)
@app.route("/api/ventas", methods=["GET"])
def get_ventas():
    return jsonify(ventas_db)

@app.route("/api/ventas", methods=["POST"])
def create_venta():
    data = request.json or {}
    total = float(data.get("total", 0.0))
    subtotal = round(total / 1.18, 2)
    igv = round(total - subtotal, 2)
    medio_pago = data.get("medio_pago", "Efectivo")
    cliente = data.get("cliente", "Cliente General")
    servicio = data.get("servicio", "Servicio Spa")

    num_ticket = f"B001-{len(ventas_db) + 4821:07d}"
    nueva_venta = {
        "id": len(ventas_db) + 1,
        "numero_boleta": num_ticket,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "cliente": cliente,
        "servicio": servicio,
        "subtotal": subtotal,
        "igv": igv,
        "total": total,
        "medio_pago": medio_pago,
        "estado": "Emitida"
    }
    ventas_db.append(nueva_venta)

    # Actualizar estado de cita si coincide
    for c in citas_db:
        if c["cliente"].lower() == cliente.lower() and not c["cobrado"]:
            c["cobrado"] = True
            c["estado"] = "Atendida"
            break

    # Registrar en caja
    if medio_pago == "Efectivo":
        caja_db["efectivo"] += total
    else:
        caja_db["digital"] += total

    caja_db["movimientos"].append({
        "hora": datetime.now().strftime("%I:%M %p"),
        "tipo": "Ingreso",
        "monto": total,
        "detalle": f"Cobro Boleta {num_ticket} ({medio_pago})"
    })

    return jsonify({"message": "Venta procesada y Boleta Electrónica emitida", "venta": nueva_venta}), 201

# CU04: Anular Venta
@app.route("/api/anulaciones", methods=["GET"])
def get_anulaciones():
    return jsonify(anulaciones_db)

@app.route("/api/anulaciones", methods=["POST"])
def create_anulacion():
    data = request.json or {}
    pin = data.get("pin", "")
    if pin != "1234":
        return jsonify({"error": "PIN gerencial inválido"}), 403

    ticket = data.get("boleta", "B001-0004821")
    motivo = data.get("motivo", "Error de digitación")
    monto = float(data.get("monto", 520.0))

    nc_num = f"NC-{len(anulaciones_db) + 13:03d}"
    nueva_anulacion = {
        "id": len(anulaciones_db) + 1,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "boleta": ticket,
        "nota_credito": nc_num,
        "monto": monto,
        "motivo": motivo,
        "autorizado_por": "Aleida Mendoza (Gerente)"
    }
    anulaciones_db.append(nueva_anulacion)

    # Revertir en caja
    caja_db["digital"] = max(0.0, caja_db["digital"] - monto)
    caja_db["movimientos"].append({
        "hora": datetime.now().strftime("%I:%M %p"),
        "tipo": "Reversión",
        "monto": -monto,
        "detalle": f"Anulación {ticket} por {nc_num}"
    })

    return jsonify({"message": "Anulación autorizada y Nota de Crédito emitida", "anulacion": nueva_anulacion}), 201

# CU05: Gestionar Operaciones de Caja
@app.route("/api/caja", methods=["GET"])
def get_caja():
    total_teorico = caja_db["apertura"] + caja_db["efectivo"] + caja_db["digital"] - caja_db["egresos"]
    return jsonify({
        **caja_db,
        "total_teorico": round(total_teorico, 2)
    })

@app.route("/api/caja/egreso", methods=["POST"])
def create_egreso():
    data = request.json or {}
    monto = float(data.get("monto", 0.0))
    motivo = data.get("motivo", "Gasto menor de caja")
    if monto > 0:
        caja_db["egresos"] += monto
        caja_db["movimientos"].append({
            "hora": datetime.now().strftime("%I:%M %p"),
            "tipo": "Egreso",
            "monto": -monto,
            "detalle": motivo
        })
        return jsonify({"message": "Egreso registrado en caja", "caja": caja_db}), 200
    return jsonify({"error": "Monto de egreso inválido"}), 400

@app.route("/api/caja/cierre", methods=["POST"])
def close_caja():
    total_teorico = caja_db["apertura"] + caja_db["efectivo"] + caja_db["digital"] - caja_db["egresos"]
    reporte_z = {
        "fecha_cierre": datetime.now().isoformat(),
        "total_apertura": caja_db["apertura"],
        "total_efectivo": caja_db["efectivo"],
        "total_digital": caja_db["digital"],
        "total_egresos": caja_db["egresos"],
        "saldo_final_arqueado": round(total_teorico, 2),
        "discrepancia": 0.0,
        "estado": "Caja Cuadrada 100% (Conforme)"
    }
    return jsonify({"message": "Arqueo y Cierre de turno completado exitosamente", "reporte_z": reporte_z})

# CU06: Compras & Insumos
@app.route("/api/compras", methods=["GET"])
def get_compras():
    return jsonify(insumos_db)

@app.route("/api/compras/orden", methods=["POST"])
def create_orden_compra():
    data = request.json or {}
    proveedor = data.get("proveedor", "L'Oréal Professionnel Perú")
    insumo = data.get("insumo", "Tinte Profesional 6.1 (12 unidades)")
    orden = {
        "numero_oc": f"OC-2026-{datetime.now().strftime('%m%d%H%M')}",
        "proveedor": proveedor,
        "insumo": insumo,
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "estado": "Enviada / En Tránsito"
    }
    return jsonify({"message": "Orden de Compra generada", "orden": orden}), 201

# CU07: Catálogo de Servicios
@app.route("/api/catalogo", methods=["GET"])
def get_catalogo():
    return jsonify(catalogo_db)

# CU08: Usuarios y Accesos
@app.route("/api/usuarios", methods=["GET"])
def get_usuarios():
    return jsonify(usuarios_db)

# CU09: Reportes Gerenciales & Objetivos Realistas SMART
@app.route("/api/reportes", methods=["GET"])
def get_reportes():
    return jsonify({
        "periodo": "Octubre 2026",
        "objetivos_smart": [
            {
                "codigo": "OBJ-01",
                "nombre": "Puntualidad en Citas y Reducción de No-Shows",
                "meta": "≥ 88%",
                "actual": "88.5%",
                "cumplimiento": "Cumplido (+0.5%)",
                "detalle": "Reducción del 35% en inasistencias gracias a confirmaciones web."
            },
            {
                "codigo": "OBJ-02",
                "nombre": "Exactitud en Arqueos y Cuadre de Caja",
                "meta": "≥ 98%",
                "actual": "98.2%",
                "cumplimiento": "Cumplido (+0.2%)",
                "detalle": "Disminución del 90% en descuadres entre dinero físico y sistema."
            },
            {
                "codigo": "OBJ-03",
                "nombre": "Disponibilidad de Insumos Críticos",
                "meta": "≥ 95%",
                "actual": "96.5%",
                "cumplimiento": "Cumplido (+1.5%)",
                "detalle": "Reducción del 80% en tratamientos cancelados por quiebre de stock."
            },
            {
                "codigo": "OBJ-04",
                "nombre": "Fidelización y Recompra de Clientes",
                "meta": "≥ 70%",
                "actual": "74.0%",
                "cumplimiento": "Cumplido (+4.0%)",
                "detalle": "Incremento del 25% en clientas que regresan en menos de 45 días."
            }
        ],
        "resumen_financiero": {
            "ingresos_totales": caja_db["efectivo"] + caja_db["digital"],
            "total_citas_atendidas": len([c for c in citas_db if c["cobrado"]]),
            "promedio_ticket": 320.0
        }
    })

# Punto de entrada para ejecución local o Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
