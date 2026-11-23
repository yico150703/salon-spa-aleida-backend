"""
Script para consultar todos los usuarios registrados en la base de datos
(Soporta PostgreSQL en Render y SQLite local automáticamente)
"""
import sys
import os

# Asegurar path al módulo backend
sys.path.insert(0, os.path.dirname(__file__))

from database import get_connection, get_cursor, is_postgres

def listar_usuarios():
    print("=" * 85)
    print("       SISTEMA SALON & SPA ALEIDA - LISTADO DE USUARIOS Y CREDENCIALES")
    motor = "PostgreSQL (Render)" if is_postgres() else "SQLite (Local)"
    print(f"       Motor de Base de Datos Activo: {motor}")
    print("=" * 85)

    conn = get_connection()
    cur = get_cursor(conn)
    
    query = """
        SELECT 
            username,
            passwordhash AS password,
            nombres,
            rol,
            dni,
            celular,
            email,
            estado
        FROM "Usuario"
        ORDER BY rol, username;
    """
    
    try:
        cur.execute(query)
        usuarios = cur.fetchall()
        
        if not usuarios:
            print("No se encontraron usuarios registrados en la base de datos.")
            return

        # Encabezado formateado
        print(f"{'USUARIO':<18} | {'CONTRASEÑA':<18} | {'ROL':<18} | {'DNI':<10} | {'NOMBRE COMPLETO'}")
        print("-" * 85)
        
        for u in usuarios:
            user = u['username'] if isinstance(u, dict) else u[0]
            pwd = (u['password'] if isinstance(u, dict) else u[1]) or '(Sin asignar)'
            nombre = u['nombres'] if isinstance(u, dict) else u[2]
            rol = u['rol'] if isinstance(u, dict) else u[3]
            dni = (u['dni'] if isinstance(u, dict) else u[4]) or '—'
            
            print(f"{user:<18} | {pwd:<18} | {rol:<18} | {dni:<10} | {nombre}")
            
        print("-" * 85)
        print(f"Total de usuarios registrados: {len(usuarios)}\n")
        
    except Exception as e:
        print(f"Error al consultar la base de datos: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    listar_usuarios()
