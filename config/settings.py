import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# Crear directorios necesarios para activos y subidas
UPLOAD_DIR = BASE_DIR / "assets" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Configuración de Base de Datos
# Por defecto utiliza SQLite local, pero si se especifica DATABASE_URL en .env, usa PostgreSQL
DB_FILE_PATH = BASE_DIR / "fitgenuss.db"
DEFAULT_SQLITE_URL = f"sqlite:///{DB_FILE_PATH}"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)

# Moneda por defecto
CURRENCY = os.getenv("FITGENUSS_CURRENCY", "S/")

# Días de anticipación para alerta de vencimiento
EXPIRY_ALERT_DAYS = int(os.getenv("FITGENUSS_EXPIRY_ALERT_DAYS", "15"))

# Categorías estándar de ingredientes
CATEGORIES = [
    "Harinas y Polvos",
    "Endulzantes Naturales",
    "Lácteos y Sustitutos",
    "Frutos Secos y Semillas",
    "Frutas y Purés",
    "Agentes de Carga y Espesantes",
    "Esencias y Chocolates",
    "Empaques y Envases",
    "Otros"
]

# Unidades soportadas
UNITS = {
    "PESO": ["mg", "g", "kg"],
    "VOLUMEN": ["ml", "l"],
    "CONTEO": ["unidad", "pack", "caja"]
}

# Unidades Base de cada Familia
BASE_UNITS = {
    "PESO": "g",
    "VOLUMEN": "ml",
    "CONTEO": "unidad"
}
