# Salon Spa Aleida - Backend API (Flask)

Servidor de API REST desarrollado en **Python / Flask**, diseñado específicamente para despliegue continuo en **[Render](https://render.com/)**.

Implementa los **9 Casos de Uso (CU01 - CU09)** y el seguimiento en tiempo real de los **4 Objetivos Estratégicos SMART** definidos para el negocio.

---

## 🚀 Despliegue en Render (Paso a Paso)

1. Sube esta carpeta `backend` a tu repositorio en GitHub (ej: `salon-spa-aleida-backend`).
2. Entra a tu cuenta en **[https://render.com](https://render.com)**.
3. Haz clic en **New +** $\rightarrow$ **Web Service**.
4. Conecta tu repositorio de GitHub.
5. Configura los siguientes campos:
   - **Name:** `salon-spa-aleida-api` (o el nombre que elijas)
   - **Environment:** `Python 3`
   - **Region:** `Oregon (US West)` o la más cercana
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** `Free`
6. Haz clic en **Create Web Service**.
7. Render te proporcionará una URL pública (ejemplo: `https://salon-spa-aleida-api.onrender.com`). Copia esa URL para configurarla en el Frontend.

---

## 💻 Ejecución en Local

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
# En Windows:
.\venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Iniciar servidor de desarrollo
python app.py
```
El servidor responderá en `http://127.0.0.1:5000/api/health`.

---

## 📡 Endpoints de la API (RESTful)

| Método | Endpoint | Caso de Uso | Descripción |
| :---: | :--- | :---: | :--- |
| `GET` | `/api/health` | - | Verificación de estado de la API y base de datos |
| `GET, POST` | `/api/citas` | `CU01` | Listado y registro de nuevas citas |
| `PUT` | `/api/citas/<id>` | `CU01` | Actualización de estado de citas |
| `GET, POST` | `/api/clientes` | `CU02` | Padrón de clientes y fichas de atención |
| `GET, POST` | `/api/ventas` | `CU03` | Emisión de boletas electrónicas con IGV 18% |
| `GET, POST` | `/api/anulaciones` | `CU04` | Emisión de Notas de Crédito con PIN |
| `GET, POST` | `/api/caja` | `CU05` | Control de saldos, egresos y arqueo con Reporte Z |
| `GET, POST` | `/api/compras` | `CU06` | Insumos críticos y órdenes de compra |
| `GET` | `/api/catalogo` | `CU07` | Catálogo de tratamientos y tarifas |
| `GET` | `/api/usuarios` | `CU08` | Usuarios y roles con permisos |
| `GET` | `/api/reportes` | `CU09` | Métricas de los 4 Objetivos SMART |
