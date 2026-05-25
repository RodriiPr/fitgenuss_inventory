from typing import List, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session
from models.ingredient import Ingredient
from models.movement import InventoryMovement
from models.supplier import Supplier
from repositories.ingredient_repository import IngredientRepository
from repositories.movement_repository import MovementRepository
from repositories.supplier_repository import SupplierRepository
from services.conversion_service import ConversionService
from config.settings import EXPIRY_ALERT_DAYS

class InventoryService:
    """
    Servicio de lógica de negocio para la gestión del inventario de FitGenuss.
    Centraliza las reglas de negocio de CRUD, actualizaciones de stock y Kárdex.
    """
    def __init__(self):
        self.ingredient_repo = IngredientRepository()
        self.movement_repo = MovementRepository()
        self.supplier_repo = SupplierRepository()

    # --- Gestión de Proveedores ---
    def get_all_suppliers(self, db: Session) -> List[Supplier]:
        """Obtiene la lista completa de proveedores."""
        return self.supplier_repo.get_all(db)

    def create_supplier(self, db: Session, name: str, contact_name: Optional[str] = None,
                        phone: Optional[str] = None, email: Optional[str] = None, 
                        address: Optional[str] = None) -> Supplier:
        """Registra un nuevo proveedor en el sistema."""
        existing = self.supplier_repo.get_by_name(db, name)
        if existing:
            raise ValueError(f"Ya existe un proveedor con el nombre '{name}'.")
        
        new_supplier = Supplier(
            name=name,
            contact_name=contact_name,
            phone=phone,
            email=email,
            address=address
        )
        return self.supplier_repo.create(db, new_supplier)

    # --- Gestión de Ingredientes (CRUD) ---
    def get_ingredient_by_id(self, db: Session, ingredient_id: int) -> Optional[Ingredient]:
        """Obtiene un ingrediente por su ID."""
        return self.ingredient_repo.get_by_id(db, ingredient_id)

    def search_ingredients(self, db: Session, query: Optional[str] = None, 
                           category: Optional[str] = None) -> List[Ingredient]:
        """Busca ingredientes con filtros aplicados."""
        return self.ingredient_repo.search(db, query, category)

    def create_ingredient(self, db: Session, name: str, category: str, unit_purchase: str,
                          unit_base: str, cantidad_compra: float, stock_minimo: float,
                          precio_compra: float, supplier_id: Optional[int] = None,
                          date_purchase: Optional[date] = None, date_expiry: Optional[date] = None,
                          image_path: Optional[str] = None) -> Ingredient:
        """
        Crea un nuevo ingrediente e inicializa su stock actual en 0.
        Calcula de forma automática el costo_unitario inicial.
        """
        existing = self.ingredient_repo.get_by_name(db, name)
        if existing:
            raise ValueError(f"Ya existe un ingrediente con el nombre '{name}'.")

        # El costo unitario inicial es el precio de compra del lote dividido por la cantidad base contenida en él
        costo_unitario = precio_compra / cantidad_compra if cantidad_compra > 0 else 0.0

        new_ingredient = Ingredient(
            name=name,
            category=category,
            unit_purchase=unit_purchase,
            unit_base=unit_base,
            cantidad_compra=cantidad_compra,
            stock_actual=0.0,  # Comienza en cero, se alimenta por movimientos
            stock_minimo=stock_minimo,
            precio_compra=precio_compra,
            costo_unitario=costo_unitario,
            supplier_id=supplier_id,
            date_purchase=date_purchase,
            date_expiry=date_expiry,
            image_path=image_path
        )
        
        return self.ingredient_repo.create(db, new_ingredient)

    def update_ingredient(self, db: Session, ingredient_id: int, name: str, category: str,
                          unit_purchase: str, unit_base: str, cantidad_compra: float,
                          stock_actual: float, stock_minimo: float, precio_compra: float,
                          supplier_id: Optional[int] = None, date_purchase: Optional[date] = None,
                          date_expiry: Optional[date] = None, image_path: Optional[str] = None) -> Ingredient:
        """Actualiza un ingrediente existente y recalcula el costo unitario."""
        ingredient = self.ingredient_repo.get_by_id(db, ingredient_id)
        if not ingredient:
            raise ValueError("Ingrediente no encontrado.")

        # Recalcular el costo unitario
        costo_unitario = precio_compra / cantidad_compra if cantidad_compra > 0 else 0.0

        # Si el stock actual cambia directamente por formulario, se actualiza
        ingredient.name = name
        ingredient.category = category
        ingredient.unit_purchase = unit_purchase
        ingredient.unit_base = unit_base
        ingredient.cantidad_compra = cantidad_compra
        ingredient.stock_actual = stock_actual
        ingredient.stock_minimo = stock_minimo
        ingredient.precio_compra = precio_compra
        ingredient.costo_unitario = costo_unitario
        ingredient.supplier_id = supplier_id
        ingredient.date_purchase = date_purchase
        ingredient.date_expiry = date_expiry
        if image_path:
            ingredient.image_path = image_path

        self.ingredient_repo.update(db, ingredient)
        return ingredient

    def delete_ingredient(self, db: Session, ingredient_id: int) -> bool:
        """Elimina un ingrediente y limpia sus registros en cascada."""
        ingredient = self.ingredient_repo.get_by_id(db, ingredient_id)
        if not ingredient:
            raise ValueError("Ingrediente no encontrado.")
        return self.ingredient_repo.delete(db, ingredient)

    # --- Gestión de Movimientos e Historial (Kárdex) ---
    def register_movement(self, db: Session, ingredient_id: int, type_movement: str,
                          quantity: float, unit: str, observation: Optional[str] = None,
                          lot_price: Optional[float] = None) -> InventoryMovement:
        """
        Registra una Entrada o Salida de stock en la base de datos.
        - Convierte la cantidad a la unidad base del ingrediente de forma automática.
        - Valida que no haya sobre-giros de stock (salidas mayores que el stock disponible).
        - Si es un movimiento de ENTRADA_COMPRA, recalcula de forma inteligente el precio de compra
          y el costo unitario según el precio pagado.
        - Actualiza el stock en la base de datos y añade la transacción al kárdex.
        """
        ingredient = self.ingredient_repo.get_by_id(db, ingredient_id)
        if not ingredient:
            raise ValueError("Ingrediente no encontrado.")

        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")

        # Convertir cantidad ingresada a la unidad base física usando el servicio de conversión
        quantity_base = ConversionService.convert(
            quantity=quantity,
            from_unit=unit,
            to_unit=ingredient.unit_base,
            conversion_factor=ingredient.cantidad_compra
        )

        is_salida = type_movement.startswith("SALIDA")

        # Validación estricta de salidas (evitar stocks negativos)
        if is_salida and ingredient.stock_actual < quantity_base:
            raise ValueError(
                f"Stock insuficiente para {ingredient.name}. "
                f"Disponible: {ingredient.stock_actual:.2f} {ingredient.unit_base}. "
                f"Requerido: {quantity_base:.2f} {ingredient.unit_base}."
            )

        # Si es una compra y se suministra el precio total del lote, recalculamos costos
        if type_movement == "ENTRADA_COMPRA" and lot_price is not None and lot_price > 0:
            # Si ingresaron en la misma unidad que la de compra:
            if unit.lower() == ingredient.unit_purchase.lower():
                # El costo por unidad de compra es precio_lote / cantidad_lotes
                price_per_purchase_unit = lot_price / quantity
                ingredient.precio_compra = price_per_purchase_unit
                ingredient.costo_unitario = price_per_purchase_unit / ingredient.cantidad_compra
            elif unit.lower() == ingredient.unit_base.lower():
                # Si ingresaron en unidad base directamente
                ingredient.costo_unitario = lot_price / quantity
                ingredient.precio_compra = ingredient.costo_unitario * ingredient.cantidad_compra
            else:
                # Si es otra unidad de la misma familia, normalizamos el precio a la unidad de compra
                price_per_base_unit = lot_price / quantity_base
                ingredient.costo_unitario = price_per_base_unit
                ingredient.precio_compra = price_per_base_unit * ingredient.cantidad_compra

        # Modificar el stock actual en el ingrediente
        if is_salida:
            ingredient.stock_actual -= quantity_base
        else:
            ingredient.stock_actual += quantity_base
            ingredient.date_purchase = date.today()

        # Registrar el movimiento en el kárdex
        new_movement = InventoryMovement(
            ingredient_id=ingredient_id,
            type_movement=type_movement,
            quantity=quantity,
            quantity_base=quantity_base,
            unit=unit,
            observation=observation
        )

        self.movement_repo.create(db, new_movement)
        self.ingredient_repo.update(db, ingredient)
        
        return new_movement

    def get_movements_history(self, db: Session, ingredient_id: Optional[int] = None) -> List[InventoryMovement]:
        """Retorna el historial completo de movimientos, opcionalmente filtrado por ingrediente."""
        if ingredient_id:
            return self.movement_repo.get_by_ingredient(db, ingredient_id)
        return self.movement_repo.get_all(db)

    def get_recent_movements(self, db: Session, limit: int = 10) -> List[InventoryMovement]:
        """Obtiene la lista de movimientos recientes para alimentar el dashboard."""
        return self.movement_repo.get_recent(db, limit)

    # --- Alertas y KPIs ---
    def get_low_stock_alerts(self, db: Session) -> List[Ingredient]:
        """Retorna los ingredientes en estado crítico de stock bajo."""
        return self.ingredient_repo.get_low_stock(db)

    def get_expiring_alerts(self, db: Session) -> List[Ingredient]:
        """Retorna los ingredientes vencidos o próximos a vencer según los días configurados."""
        return self.ingredient_repo.get_expiring_soon(db, EXPIRY_ALERT_DAYS)

    def get_dashboard_kpis(self, db: Session) -> dict:
        """
        Calcula y agrupa los KPIs clave del inventario.
        """
        all_ingredients = self.ingredient_repo.get_all(db)
        total_ingredients = len(all_ingredients)
        low_stock_count = len(self.get_low_stock_alerts(db))
        expiring_count = len(self.get_expiring_alerts(db))
        total_valuation = self.ingredient_repo.get_total_valuation(db)

        return {
            "total_ingredients": total_ingredients,
            "low_stock_count": low_stock_count,
            "expiring_count": expiring_count,
            "total_valuation": total_valuation
        }
