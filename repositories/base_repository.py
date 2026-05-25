from typing import TypeVar, Generic, Type, List, Optional
from sqlalchemy.orm import Session
from models.base import Base

T = TypeVar('T', bound=Base)

class BaseRepository(Generic[T]):
    """
    Repositorio base genérico para realizar operaciones CRUD comunes.
    Sigue buenas prácticas de diseño y reduce la duplicación de código.
    """
    def __init__(self, model: Type[T]):
        self.model = model

    def get_by_id(self, db: Session, id_val: int) -> Optional[T]:
        """Obtiene un registro por su ID primary key."""
        return db.query(self.model).filter(self.model.id == id_val).first()

    def get_all(self, db: Session) -> List[T]:
        """Obtiene todos los registros de la tabla."""
        return db.query(self.model).all()

    def create(self, db: Session, obj: T) -> T:
        """Agrega un nuevo registro y realiza el flush para obtener su ID generado."""
        db.add(obj)
        db.flush()
        return obj

    def update(self, db: Session, obj: T) -> T:
        """Actualiza el registro en la sesión."""
        db.add(obj)
        db.flush()
        return obj

    def delete(self, db: Session, obj: T) -> bool:
        """Elimina el registro de la base de datos."""
        try:
            db.delete(obj)
            db.flush()
            return True
        except Exception:
            return False
