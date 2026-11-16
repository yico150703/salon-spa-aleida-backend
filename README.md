# Salón & Spa Aleida - Backend API (Flask & PostgreSQL en Render)

Servidor de API RESTful desarrollado en **Python / Flask** con persistencia en **PostgreSQL**, diseñado para despliegue automatizado en **[Render](https://render.com/)**.

Implementa los **9 Casos de Uso (CU01 - CU09)**, la arquitectura multicapa (Presentación $\rightarrow$ Control $\rightarrow$ DAO $\rightarrow$ PostgreSQL) y el monitoreo de los **4 Objetivos Estratégicos SMART**.

---

## 🏗️ Arquitectura de la Solución

* **Framework:** Flask 3.0 / Gunicorn
* **Motor de Base de Datos:** PostgreSQL en Render (con fallback a SQLite para desarrollo local offline)
* **Patrón de Persistencia:** Composite DAO / Repository Pattern (Capa 3 de la Sección 3.8 del documento)
* **Infraestructura como Código (IaC):** `render.yaml` (Blueprint para creación simultánea de Web Service + PostgreSQL)

---

## 🚀 Despliegue en Render con PostgreSQL

### Opción A: Despliegue Automatizado con Blueprint (`render.yaml`)

1. Sube tu código a un repositorio en **GitHub**.
2. Ingresa a **[Render.com](https://render.com/)**.
3. En el panel principal, haz clic en **New +** $\rightarrow$ **Blueprint**.
4. Conecta tu repositorio. Render detectará automáticamente el archivo `render.yaml` y creará:
   * 🐘 **Base de Datos Gestionada:** `spa-aleida-db` (PostgreSQL)
   * 🌐 **Servicio Web:** `spa-aleida-api` (Flask API con `DATABASE_URL` conectada automáticamente)
5. Haz clic en **Apply**. ¡Las tablas y datos semilla se crearán solos al arrancar!

---

### Opción B: Despliegue Manual Paso a Paso

#### 1. Crear la Base de Datos PostgreSQL en Render
1. En Render, haz clic en **New +** $\rightarrow$ **PostgreSQL**.
2. Configura:
   * **Name:** `spa-aleida-db`
   * **Database:** `spa_aleida`
   * **User:** `spa_user`
   * **Region:** `Oregon (US West)` (o la misma de tu frontend)
   * **Plan:** `Free`
3. Haz clic en **Create Database**.
4. En la pestaña de la base de datos creada, copia la **Internal Database URL** (o External si te conectas desde fuera).

#### 2. Crear el Web Service en Render
1. Haz clic en **New +** $\rightarrow$ **Web Service**.
2. Conecta tu repositorio de GitHub.
3. Configura:
   * **Name:** `salon-spa-aleida-api`
   * **Root Directory:** `backend` (o déjalo en blanco si el repo es solo la carpeta backend)
   * **Environment:** `Python 3`
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `gunicorn app:app`
4. En la sección **Environment Variables**, añade:
   * `DATABASE_URL` = *(pega aquí la Database URL de tu PostgreSQL en Render)*
   * `PYTHON_VERSION` = `3.11.8`
5. Haz clic en **Create Web Service**.

Al iniciar, el servidor ejecutará `init_db()` automáticamente, creando todas las tablas relacionales y cargando el catálogo de tratamientos, terapeutas y usuarios iniciales.

---

## 💻 Ejecución en Local (Desarrollo)

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
# En Windows:
.\venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. (Opcional) Si quieres probar con PostgreSQL local:
# set DATABASE_URL=postgresql://usuario:clave@localhost:5432/spa_aleida

# 5. Iniciar servidor
python app.py
```
> *Nota:* Si `DATABASE_URL` no está definida, el backend usa automáticamente SQLite (`spa_aleida.db`) sin requerir instalar servidores adicionales.

---

## 📡 Endpoints de la API REST

| Método | Endpoint | Caso de Uso | Descripción |
| :---: | :--- | :---: | :--- |
| `GET` | `/api/health` | - | Verificación de estado del servidor y motor de BD activo |
| `GET` | `/api/db-status` | - | Conectividad de PostgreSQL y conteo de registros en tablas |
| `GET` | `/api/arquitectura/trace` | - | Inspector didáctico de flujo por las 4 capas (MVC + DAO) |
| `GET, POST` | `/api/citas` | `CU01` | Listado y registro de citas con validación de no-colisión |
| `PUT` | `/api/citas/<id>/reprogramar`| `CU01` | Reprogramación de fecha y hora |
| `PUT` | `/api/citas/<id>/estado` | `CU01` | Cambio de estado (Confirmada, Atendida, Cancelada) |
| `GET, POST` | `/api/clientes` | `CU02` | Padrón de clientes y fichas estéticas |
| `GET, POST` | `/api/ventas` | `CU03` | Emisión de boletas electrónicas con IGV 18% |
| `GET, POST` | `/api/anulaciones` | `CU04` | Emisión de Notas de Crédito con autorización gerencial |
| `GET` | `/api/caja` | `CU05` | Consulta de estado de caja chica y movimientos |
| `POST` | `/api/caja/egreso` | `CU05` | Registro de egresos menores de caja |
| `POST` | `/api/caja/cierre` | `CU05` | Conciliación física, arqueo y emisión de Reporte Z |
| `GET` | `/api/compras` | `CU06` | Insumos críticos y alertas de stock mínimo |
| `POST` | `/api/compras/orden` | `CU06` | Generación de Órdenes de Compra a proveedores |
| `GET` | `/api/catalogo` | `CU07` | Catálogo de tratamientos y tarifas vigentes |
| `GET` | `/api/usuarios` | `CU08` | Usuarios, roles y control de acceso |
| `GET` | `/api/reportes` | `CU09` | Cumplimiento de los 4 Objetivos SMART en tiempo real |
