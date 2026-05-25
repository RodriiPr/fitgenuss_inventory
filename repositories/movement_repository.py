from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from models.movement import InventoryMovement
from repositories.base_repository import BaseRepository

class MovementRepository(BaseRepository[InventoryMovement]):
    """
    Repositorio para el modelo InventoryMovement.
    Encapsula consultas sobre el historial de movimientos y kárdex.
    """
    def __init__(self):
        super().__init__(InventoryMovement)

    def get_by_ingredient(self, db: Session, ingredient_id: int) -> List[InventoryMovement]:
        """Obtiene todos los movimientos asociados a un ingrediente específico, ordenados de más reciente a más antiguo."""
        return db.query(InventoryMovement).filter(
            InventoryMovement.ingredient_id == ingredient_id
        ).order_by(InventoryMovement.date.desc()).all()

    def get_by_date_range(self, db: Session, start_date: datetime, end_date: datetime) -> List[InventoryMovement]:
        """Obtiene los movimientos registrados dentro de un rango de fechas."""
        return db.query(InventoryMovement).filter(
            InventoryMovement.date >= start_date,
            InventoryMovement.date <= end_date
        ).order_by(InventoryMovement.date.desc()).all()

    def get_recent(self, db: Session, limit: int = 10) -> List[InventoryMovement]:
        """Retorna los últimos N movimientos para mostrar en el feed del dashboard."""
        return db.query(InventoryMovement).order_by(InventoryMovement.date.desc()).limit(limit).all()
