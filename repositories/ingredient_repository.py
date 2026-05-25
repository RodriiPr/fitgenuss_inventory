from typing import List, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.ingredient import Ingredient
from repositories.base_repository import BaseRepository

class IngredientRepository(BaseRepository[Ingredient]):
    """
    Repositorio para el modelo Ingredient.
    Encapsula consultas específicas de ingredientes, alertas de stock y de vencimiento.
    """
    def __init__(self):
        super().__init__(Ingredient)

    def get_by_name(self, db: Session, name: str) -> Optional[Ingredient]:
        """Busca un ingrediente por su nombre exacto."""
        return db.query(Ingredient).filter(Ingredient.name.ilike(name)).first()

    def search(self, db: Session, query: Optional[str] = None, category: Optional[str] = None) -> List[Ingredient]:
        """
        Busca ingredientes aplicando filtros por nombre/proveedor y/o categoría.
        """
        q = db.query(Ingredient)
        if query:
            search_filter = f"%{query}%"
            q = q.filter(
                or_(
                    Ingredient.name.ilike(search_filter),
                    Ingredient.category.ilike(search_filter)
                )
            )
        if category and category != "Todos":
            q = q.filter(Ingredient.category == category)
        return q.order_by(Ingredient.name).all()

    def get_low_stock(self, db: Session) -> List[Ingredient]:
        """Retorna ingredientes cuyo stock actual es menor o igual al mínimo establecido."""
        return db.query(Ingredient).filter(Ingredient.stock_actual <= Ingredient.stock_minimo).all()

    def get_expiring_soon(self, db: Session, days: int) -> List[Ingredient]:
        """
        Retorna ingredientes que están vencidos o vencerán en los próximos N días.
        """
        limit_date = date.today() + timedelta(days=days)
        return db.query(Ingredient).filter(
            Ingredient.date_expiry.isnot(None),
            Ingredient.date_expiry <= limit_date
        ).order_by(Ingredient.date_expiry).all()
        
    def get_total_valuation(self, db: Session) -> float:
        """Calcula el valor monetario total actual del inventario (stock * costo_unitario)."""
        ingredients = self.get_all(db)
        return sum((ing.stock_actual * ing.costo_unitario) for ing in ingredients)
