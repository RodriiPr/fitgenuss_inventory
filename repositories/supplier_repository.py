from typing import Optional
from sqlalchemy.orm import Session
from models.supplier import Supplier
from repositories.base_repository import BaseRepository

class SupplierRepository(BaseRepository[Supplier]):
    """
    Repositorio para el modelo Supplier.
    Encapsula consultas específicas de proveedores.
    """
    def __init__(self):
        super().__init__(Supplier)

    def get_by_name(self, db: Session, name: str) -> Optional[Supplier]:
        """Busca un proveedor por su nombre exacto."""
        return db.query(Supplier).filter(Supplier.name.ilike(name)).first()
