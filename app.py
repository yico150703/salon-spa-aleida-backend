"""
=============================================================================
SALON SPA ALEIDA - APLICACIÓN PRINCIPAL (FLASK BACKEND)
Punto de Entrada del Servidor Web (Render & Local)
Organizado bajo Arquitectura por Capas (MVC + DAO) conforme a la Sección 3.8
=============================================================================
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from database import init_db
from controllers.routes import api_bp

def create_app():
    # Inicializar Base de Datos (PostgreSQL en Render o SQLite local)
    try:
        init_db()
    except Exception as e:
        print(f"[WARN] Error inicializando base de datos: {e}")

    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Registrar Blueprint de Controladores (Capa 1)
    app.register_blueprint(api_bp)

    @app.route("/", methods=["GET"])
    def root():
        return jsonify({
            "app": "Salon Spa Aleida - Backend API",
            "arquitectura": "4 Capas: Presentación -> Control/Negocio -> Acceso a Datos (DAO) -> Entidades DB",
            "patron": "MVC + Composite DAO (Sección 3.8 del Documento)",
            "despliegue": "Render Web Service",
            "version": "2.1.0",
            "health_check": "/api/health",
            "live_architecture_trace": "/api/arquitectura/trace"
        })

    return app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
