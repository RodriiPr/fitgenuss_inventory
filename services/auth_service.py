import bcrypt
from typing import Optional, List
from sqlalchemy.orm import Session
from models.user import User
from repositories.user_repository import UserRepository

class AuthService:
    """
    Servicio de autenticación y seguridad para FitGenuss.
    Utiliza bcrypt para realizar hashes de contraseñas de forma robusta e irreversible.
    """
    def __init__(self):
        self.user_repo = UserRepository()

    def hash_password(self, password: str) -> str:
        """Genera un hash bcrypt seguro para una contraseña en texto plano."""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verifica si una contraseña coincide con su hash almacenado."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False

    def authenticate(self, db: Session, username: str, password: str) -> Optional[User]:
        """
        Valida las credenciales de un usuario.
        
        Returns:
            El objeto User si la autenticación es exitosa, None en caso contrario.
        """
        user = self.user_repo.get_by_username(db, username)
        if not user:
            return None
        
        if self.verify_password(password, user.password_hash):
            return user
        return None

    def get_users(self, db: Session) -> List[User]:
        """Obtiene todos los usuarios registrados ordenados por nombre."""
        return self.user_repo.get_all_ordered(db)

    def create_user(self, db: Session, username: str, password: str, name: str, role: str = "admin") -> User:
        """Crea y registra un nuevo usuario en la base de datos aplicando hash a su contraseña."""
        clean_username = username.strip().lower()
        clean_name = name.strip()

        if not clean_username:
            raise ValueError("El usuario es obligatorio.")
        if not clean_name:
            raise ValueError("El nombre es obligatorio.")
        if len(password) < 4:
            raise ValueError("La contraseña debe tener al menos 4 caracteres.")
        if self.user_repo.get_by_username(db, clean_username):
            raise ValueError("Ese nombre de usuario ya existe.")

        hashed = self.hash_password(password)
        new_user = User(
            username=clean_username,
            password_hash=hashed,
            name=clean_name,
            role=role
        )
        return self.user_repo.create(db, new_user)

    def update_password(self, db: Session, user_id: int, new_password: str) -> User:
        """Actualiza la contraseña de un usuario existente."""
        if len(new_password) < 4:
            raise ValueError("La contraseña debe tener al menos 4 caracteres.")

        user = self.user_repo.get_by_id(db, user_id)
        if not user:
            raise ValueError("Usuario no encontrado.")

        user.password_hash = self.hash_password(new_password)
        return self.user_repo.update(db, user)
