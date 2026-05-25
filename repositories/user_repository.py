from typing import Optional, List
from sqlalchemy.orm import Session
from models.user import User
from repositories.base_repository import BaseRepository

class UserRepository(BaseRepository[User]):
    """
    Repositorio para el modelo User.
    Encapsula consultas específicas de usuarios.
    """
    def __init__(self):
        super().__init__(User)

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Busca un usuario por su nombre de usuario de manera insensible a mayúsculas/minúsculas."""
        return db.query(User).filter(User.username.ilike(username)).first()

    def get_all_ordered(self, db: Session) -> List[User]:
        """Lista todos los usuarios ordenados por nombre."""
        return db.query(User).order_by(User.name.asc()).all()
