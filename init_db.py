"""
Script de inicialización y migración para PostgreSQL / Render
Ejecutar con: python init_db.py
"""
import os
import sys
from database import init_db, is_postgres, get_connection

if __name__ == "__main__":
    print("==================================================")
    print("SALÓN & SPA ALEIDA - INICIALIZADOR DE BASE DE DATOS")
    print(f"Motor Detectado: {'PostgreSQL en Render' if is_postgres() else 'SQLite Local'}")
    print("==================================================")
    try:
        init_db()
        print("✓ Tablas creadas y datos maestros cargados exitosamente.")
    except Exception as e:
        print(f"✗ Error durante la inicialización: {e}")
        sys.exit(1)
