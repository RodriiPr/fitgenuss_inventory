# FitGenuss - Sistema Inteligente de Control de Inventario 🍰

Bienvenido al sistema de control de inventario profesional y modular desarrollado para **FitGenuss**, un negocio premium de repostería saludable y postres fit.

Este sistema ha sido diseñado por un arquitecto de software senior siguiendo buenas prácticas de ingeniería de software, arquitectura limpia en capas, principios **SOLID** y el principio **DRY (Don't Repeat Yourself)**. Está completamente desacoplado y preparado para escalar sin fricciones a un ERP o SaaS completo (con módulos de recetas, producción automatizada, ventas POS, finanzas y multi-sucursal).

---

## 🎨 Diseño Visual Premium y Estética
La interfaz del sistema ha sido curada con una paleta de colores moderna inspirada en la salud y la repostería fina:
- **Verde Matcha (`#7CB342`)**: El color primario, representa ingredientes naturales, fitness y vitalidad.
- **Rosa Pastel (`#FF8A80`)**: El color secundario, representa la dulzura, repostería y la atención al detalle gourmet.
- **Glassmorphism sutil**: Tarjetas KPI blancas con sombras dinámicas de profundidad y bordes resplandecientes al pasar el cursor (hover).
- **Tipografía moderna**: Outfit e Inter cargadas dinámicamente desde Google Fonts.

---

## 🏗️ Arquitectura de Software (Estructura por Capas)

El código fuente está modularizado en carpetas independientes para aislar responsabilidades. Esto permite realizar cambios en la base de datos o en la interfaz gráfica sin comprometer la lógica de negocio básica:

```
fitgenuss_inventory/
├── app.py                      # Enrutador principal e inicializador de Streamlit
├── requirements.txt            # Dependencias de librerías Python
├── .env                        # Configuración de variables de entorno
├── config/
│   └── settings.py             # Parámetros centralizados de categorías, unidades y rutas
├── database/
│   ├── connection.py           # Conexión SQLAlchemy (soporta SQLite local y PostgreSQL)
│   └── initial_data.py         # Creador automático de tablas y carga de datos demo
├── models/
│   ├── base.py                 # Declarativa Base común de ORM
│   ├── user.py                 # Mapeo de usuarios administradores
│   ├── supplier.py             # Mapeo de proveedores de ingredientes
│   ├── ingredient.py           # Mapeo de ingredientes (stock base, mínimos, costos)
│   └── movement.py             # Mapeo de transacciones de Kárdex (entradas y salidas)
├── repositories/
│   ├── base_repository.py      # Operaciones CRUD genéricas con tipos dinámicos (Generics)
│   ├── user_repository.py      # Consultas y queries específicas de usuarios
│   ├── supplier_repository.py  # Consultas específicas de proveedores
│   ├── ingredient_repository.py# Filtros de stock, alertas y valoración total
│   └── movement_repository.py  # Consultas de movimientos por fechas e ingredientes
├── services/
│   ├── auth_service.py         # Seguridad, hashes de contraseñas con bcrypt y login
│   ├── conversion_service.py   # Lógica inteligente de equivalencias multi-unidad
│   ├── inventory_service.py    # Lógica de negocio (ajuste de stocks, validación de quiebres)
│   └── report_service.py       # Generador de reportes ejecutivos en PDF y Excel
├── utils/
│   └── styles.py               # Inyección de hojas de estilo CSS personalizadas
└── modules/
    ├── login_view.py           # Pantalla de acceso seguro
    ├── dashboard_view.py       # Visualización de KPIs y gráficos interactivos Plotly
    ├── inventory_view.py       # Interfaz CRUD del catálogo de ingredientes
    ├── movements_view.py       # Interfaz de registro de Kárdex de stock
    ├── alerts_view.py          # Panel de alertas de stock mínimo y vencimientos
    └── reports_view.py         # Descargas y herramientas de backups manuales
```

---

## 🌟 Funcionalidades Destacadas

1. **⚖️ Inventario Multi-Unidad Inteligente**:
   - Compra y almacena ingredientes en unidades comerciales (ej. sacos en `kg`, botellas en `l`, empaques en `pack`).
   - Registre sus consumos o salidas en la unidad de preparación granular (ej. `g`, `ml`, `unidad`).
   - El sistema calcula equivalencias de forma 100% automática y normaliza todo en la **Unidad Base** dentro de la base de datos.
2. **📈 Dashboard Ejecutivo Plotly**:
   - Tarjetas KPI con sombreado dinámico para valorización, stock y vencimiento.
   - Gráfico interactivo de dona para observar la distribución del capital invertido en stock por categorías.
   - Histograma del inventario físico.
3. **💸 Recalculación Automática de Costos**:
   - Al registrar una entrada de compra (`ENTRADA_COMPRA`) ingresando el precio pagado por el lote, el sistema recalcula inmediatamente el `costo_unitario` por unidad base (ej: costo por gramo) y actualiza el valor del catálogo de forma transparente.
4. **🔔 Centro de Control de Alertas**:
   - Alertas visuales con barras de progreso para ingredientes en quiebre de stock mínimo.
   - Botón automático **mailto** para redactar correos automáticos pre-configurados a los proveedores en un solo clic.
   - Fechas de vencimiento con clasificación de colores (rojo: vencido, naranja: por vencer en menos de 15 días).
5. **📊 Descarga de Reportes y Backups Calientes**:
   - Generación al vuelo de hojas de cálculo de Excel (.xlsx) estilizadas y reportes de PDF ejecutivos con membrete de marca de agua de **FitGenuss**.
   - Copia de seguridad en caliente de la base de datos local (.db) empaquetada con estampas de tiempo en `assets/backups/`.

---

## ⚙️ Instrucciones de Instalación y Ejecución

Siga estos sencillos pasos en su terminal de Windows para poner en marcha la aplicación localmente:

### 1. Clonar o descargar el proyecto e ingresar al directorio
Abra PowerShell o Command Prompt (CMD) en la carpeta del proyecto:
```powershell
cd "C:\\Users\\André Rodríguez\\.gemini\\antigravity\\scratch\\fitgenuss_inventory"
```

### 2. Crear y activar un entorno virtual de Python (Recomendado)
```powershell
# Crear entorno virtual
python -m venv venv

# Activar en PowerShell
.\\venv\\Scripts\\Activate.ps1

# O activar en CMD estándar
.\\venv\\Scripts\\activate.bat
```

### 3. Instalar dependencias
Instale todas las librerías necesarias especificadas en el archivo `requirements.txt`:
```powershell
pip install -r requirements.txt
```

### 4. Ejecutar la Aplicación Streamlit
Lance el servidor de desarrollo local de Streamlit:
```powershell
streamlit run app.py
```
*La aplicación se abrirá de forma automática en su navegador en `http://localhost:8501`.*

---

## 🔑 Credenciales de Acceso por Defecto
El sistema autodetecta si la base de datos está vacía y la siembra automáticamente con datos reales de prueba y una cuenta administrativa segura inicial:
- **Usuario**: `admin`
- **Contraseña**: `admin`

Usuarios adicionales creados automáticamente para operación compartida:
- **Usuario**: `andre` | **Contraseña**: `andre123`
- **Usuario**: `angeles` | **Contraseña**: `angeles123`
 
*(Una vez dentro, puede interactuar con el catálogo, modificar stock o registrar nuevos movimientos).*

---

## 🚀 Preparado para el Futuro: Hoja de Ruta ERP & SaaS
Este inventario modular es la base de un ERP integral. A continuación se describe cómo se diseñó para escalar en las siguientes etapas:

1. **Recetas y Producción (BOM)**:
   - Se puede crear una tabla `recipes` (id, name, description) y `recipe_ingredients` (recipe_id, ingredient_id, quantity_base).
   - Al registrar una producción de "Cheesecake de Plátano Fit", el servicio de producción consumirá automáticamente del inventario restando las cantidades de ingredientes exactas en base a la receta, usando nuestro `InventoryService.register_movement()` con tipo `SALIDA_USO`.
2. **Punto de Venta (POS) y Ventas**:
   - Crear un modelo `Order` y `OrderItem` para registrar ventas. Al cerrar una orden de venta de postres, se dispara un trigger en la capa de servicios para deducir el stock del postre (si es un producto empacado) o de sus ingredientes correspondientes.
3. **Multiusuario y Roles**:
   - El modelo `User` ya cuenta con el campo `role` ('admin', 'supervisor'). La capa de vistas de Streamlit está lista para condicionar formularios de edición o eliminación ocultándolos para roles con menor jerarquía como operarios de cocina.
4. **Múltiples Sucursales**:
   - Se puede agregar un modelo `Branch` y añadir `branch_id` en las tablas `ingredients` e `inventory_movements`, aislando el stock de Avena o Envases por establecimiento físico y consolidando reportes financieros globales en el dashboard.
