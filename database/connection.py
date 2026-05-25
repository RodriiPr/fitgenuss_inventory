from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from contextlib import contextmanager
from config.settings import DATABASE_URL

# Sanitizar URL para PostgreSQL (SQLAlchemy 2.0 requiere obligatoriamente 'postgresql://' en vez de 'postgres://')
DB_URL = DATABASE_URL
if DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

# Crear el motor de la base de datos (con soporte para hilos en SQLite si es el caso)
connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}

engine = create_engine(
    DB_URL,
    connect_args=connect_args,
    pool_pre_ping=True,  # Auto-reconexión si el servidor de BD se apaga
)

# Sesión fábrica local
session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = scoped_session(session_factory)

# Declarativa base para los modelos ORM
Base = declarative_base()

@contextmanager
def get_db():
    """
    Context manager para obtener una sesión de base de datos segura.
    Garantiza que la sesión se cierre correctamente tras su uso
    y maneja la reversión (rollback) en caso de errores.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def init_db():
    """
    Crea todas las tablas definidas en los modelos si aún no existen.
    """
    # Importar los modelos aquí para asegurar que estén registrados en Base antes de crearlos
    import models.user
    import models.supplier
    import models.ingredient
    import models.movement
    
    Base.metadata.create_all(bind=engine)
