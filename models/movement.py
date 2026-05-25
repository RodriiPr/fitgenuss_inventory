from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base

class InventoryMovement(Base):
    __tablename__ = 'inventory_movements'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    type_movement = Column(String(30), nullable=False)  # ENTRADA_COMPRA, ENTRADA_REPOSICION, SALIDA_USO, SALIDA_PERDIDA, SALIDA_MERMA
    ingredient_id = Column(Integer, ForeignKey('ingredients.id'), nullable=False)
    
    quantity = Column(Float, nullable=False)        # Cantidad ingresada por el usuario (ej. 2)
    quantity_base = Column(Float, nullable=False)   # Cantidad normalizada en unidad base (ej. 2000)
    unit = Column(String(20), nullable=False)        # Unidad ingresada (ej. kg)
    
    observation = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    ingredient = relationship("Ingredient", back_populates="movements")

    def __repr__(self):
        return f"<InventoryMovement(type='{self.type_movement}', ingredient_id='{self.ingredient_id}', qty_base='{self.quantity_base}')>"
