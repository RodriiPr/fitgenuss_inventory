from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base

class Ingredient(Base):
    __tablename__ = 'ingredients'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # Harinas y Polvos, Endulzantes, Lácteos, etc.
    
    # Manejo de multi-unidad
    unit_purchase = Column(String(20), nullable=False)  # kg, l, pack, caja, unidad
    unit_base = Column(String(20), nullable=False)      # g, ml, unidad, mg
    cantidad_compra = Column(Float, nullable=False, default=1.0) # Factor de conversión (ej. 1 kg = 1000 g)
    
    # Cantidades y stocks siempre almacenados en UNIDAD BASE
    stock_actual = Column(Float, default=0.0)
    stock_minimo = Column(Float, default=0.0)
    
    # Precios y costos
    precio_compra = Column(Float, default=0.0)  # Precio pagado por una UNIDAD DE COMPRA (ej. 1 kg)
    costo_unitario = Column(Float, default=0.0) # Costo por UNIDAD BASE = precio_compra / cantidad_compra
    
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=True)
    date_purchase = Column(Date, nullable=True)
    date_expiry = Column(Date, nullable=True)
    image_path = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    supplier = relationship("Supplier", back_populates="ingredients")
    movements = relationship("InventoryMovement", back_populates="ingredient", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Ingredient(name='{self.name}', stock='{self.stock_actual} {self.unit_base}', cost='{self.costo_unitario}')>"
