import logging
from datetime import date, timedelta
from sqlalchemy.orm import Session
from database.connection import get_db, init_db
from services.auth_service import AuthService
from services.inventory_service import InventoryService
from models.user import User
from models.supplier import Supplier
from models.ingredient import Ingredient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_database():
    """
    Puebla la base de datos con datos de prueba realistas si está vacía.
    Esto permite que la aplicación inicie con KPIs, gráficos y Kárdex listos para usar.
    """
    logger.info("Iniciando inicialización de la base de datos...")
    
    # Asegurar que las tablas existan
    init_db()
    
    auth_service = AuthService()
    inv_service = InventoryService()
    
    with get_db() as db:
        # 1. Crear usuarios base si no existen
        base_users = [
            {"username": "admin", "password": "admin", "name": "André (Chef FitGenuss)", "role": "admin"},
            {"username": "andre", "password": "andre123", "name": "André", "role": "admin"},
            {"username": "angeles", "password": "angeles123", "name": "Angeles", "role": "admin"},
        ]

        for base_user in base_users:
            existing_user = db.query(User).filter(User.username == base_user["username"]).first()
            if not existing_user:
                logger.info(f"Creando usuario base {base_user['username']}...")
                auth_service.create_user(
                    db=db,
                    username=base_user["username"],
                    password=base_user["password"],
                    name=base_user["name"],
                    role=base_user["role"]
                )

        # 2. Registrar Proveedores demo si la tabla está vacía
        if db.query(Supplier).count() == 0:
            logger.info("Poblando proveedores demo...")
            sup1 = inv_service.create_supplier(db, "Molinos Healthy Co.", "Carlos Ramos", "+51 987654321", "carlos@molinoshealthy.com", "Av. Industrial 124, Lima")
            sup2 = inv_service.create_supplier(db, "GreenSweet Co. (Organics)", "Lucía Fernández", "+51 912345678", "contacto@greensweet.pe", "Calle Las Dalias 445, Miraflores")
            sup3 = inv_service.create_supplier(db, "EcoPack Peru S.A.", "Martín Prado", "+51 999888777", "ventas@ecopack.com.pe", "Av. Los Rosales 890, Ate")
            sup4 = inv_service.create_supplier(db, "Lácteos Fit & Co.", "Elena Gómez", "+51 955444333", "egomez@lacteosfit.com", "Carretera Central Km 12.5, Chosica")
            db.flush()
        
        # Recuperar proveedores de la base de datos para mapear sus IDs
        sups = db.query(Supplier).all()
        suppliers_map = {s.name: s.id for s in sups}

        # 3. Registrar Ingredientes demo si la tabla está vacía
        if db.query(Ingredient).count() == 0:
            logger.info("Poblando ingredientes demo...")
            
            # Ingrediente Avena (Peso: kg -> g)
            ing_avena = inv_service.create_ingredient(
                db=db,
                name="Avena en Hojuelas Integral",
                category="Harinas y Polvos",
                unit_purchase="kg",
                unit_base="g",
                cantidad_compra=1000.0,
                stock_minimo=1500.0,
                precio_compra=8.50,
                supplier_id=suppliers_map["Molinos Healthy Co."],
                date_purchase=date.today() - timedelta(days=20),
                date_expiry=date.today() + timedelta(days=90)
            )

            # Ingrediente Yogurt Griego (Volumen: l -> ml)
            ing_yogurt = inv_service.create_ingredient(
                db=db,
                name="Yogurt Griego Natural 0% Grasa",
                category="Lácteos y Sustitutos",
                unit_purchase="l",
                unit_base="ml",
                cantidad_compra=1000.0,
                stock_minimo=2000.0,
                precio_compra=14.90,
                supplier_id=suppliers_map["Lácteos Fit & Co."],
                date_purchase=date.today() - timedelta(days=10),
                date_expiry=date.today() + timedelta(days=8)  # Próximo a vencer
            )

            # Ingrediente Stevia (Conteo/Volumen: Botella/pack -> ml)
            ing_stevia = inv_service.create_ingredient(
                db=db,
                name="Stevia Líquida Concentrada 250ml",
                category="Endulzantes Naturales",
                unit_purchase="pack",  # Comprada en botellas individuales
                unit_base="ml",
                cantidad_compra=250.0,  # 1 botella tiene 250ml
                stock_minimo=150.0,
                precio_compra=28.00,
                supplier_id=suppliers_map["GreenSweet Co. (Organics)"],
                date_purchase=date.today() - timedelta(days=15),
                date_expiry=date.today() + timedelta(days=120)
            )

            # Ingrediente Envases Kraft (Conteo: pack -> unidad)
            ing_envase = inv_service.create_ingredient(
                db=db,
                name="Envase Kraft Eco para Postre 8oz",
                category="Empaques y Envases",
                unit_purchase="pack",  # Viene en paquetes de 50
                unit_base="unidad",
                cantidad_compra=50.0,  # 1 paquete = 50 envases
                stock_minimo=40.0,
                precio_compra=35.00,
                supplier_id=suppliers_map["EcoPack Peru S.A."],
                date_purchase=date.today() - timedelta(days=30),
                date_expiry=None  # No vence
            )
            
            # Ingrediente Harina de Almendras (Peso: kg -> g)
            ing_almendra = inv_service.create_ingredient(
                db=db,
                name="Harina de Almendras Fina",
                category="Harinas y Polvos",
                unit_purchase="kg",
                unit_base="g",
                cantidad_compra=1000.0,
                stock_minimo=800.0,
                precio_compra=42.00,
                supplier_id=suppliers_map["Molinos Healthy Co."],
                date_purchase=date.today() - timedelta(days=5),
                date_expiry=date.today() - timedelta(days=2)  # ¡VENCIDO!
            )
            db.flush()
            
            # Recuperar los ingredientes recién guardados para alimentar el Kárdex con compras y salidas
            ings = db.query(Ingredient).all()
            ings_map = {i.name: i.id for i in ings}

            logger.info("Alimentando Kárdex inicial con transacciones...")
            
            # 4. Registrar Entradas por Compra (Alimentar inventario)
            inv_service.register_movement(db, ings_map["Avena en Hojuelas Integral"], "ENTRADA_COMPRA", 5.0, "kg", "Compra de lote de avena inicial", lot_price=42.50)
            inv_service.register_movement(db, ings_map["Yogurt Griego Natural 0% Grasa"], "ENTRADA_COMPRA", 8.0, "l", "Compra inicial de yogurt griego", lot_price=119.20)
            inv_service.register_movement(db, ings_map["Stevia Líquida Concentrada 250ml"], "ENTRADA_COMPRA", 3.0, "pack", "Compra de 3 botellas de stevia", lot_price=84.00)
            inv_service.register_movement(db, ings_map["Envase Kraft Eco para Postre 8oz"], "ENTRADA_COMPRA", 2.0, "pack", "Compra de 2 paquetes de envases (100 u)", lot_price=70.00)
            inv_service.register_movement(db, ings_map["Harina de Almendras Fina"], "ENTRADA_COMPRA", 1.5, "kg", "Compra inicial de harina de almendras", lot_price=63.00)
            
            # 5. Registrar Salidas (Consumos, Mermas)
            inv_service.register_movement(db, ings_map["Avena en Hojuelas Integral"], "SALIDA_USO", 450.0, "g", "Consumo en producción de Muffins de Plátano Fit")
            inv_service.register_movement(db, ings_map["Avena en Hojuelas Integral"], "SALIDA_USO", 300.0, "g", "Consumo en producción de Galletas de Avena & Chispas")
            inv_service.register_movement(db, ings_map["Yogurt Griego Natural 0% Grasa"], "SALIDA_USO", 1500.0, "ml", "Consumo para base cremosa de Cheesecakes Proteicos")
            inv_service.register_movement(db, ings_map["Stevia Líquida Concentrada 250ml"], "SALIDA_USO", 80.0, "ml", "Endulzado de Cheesecakes y Brownies Fit")
            inv_service.register_movement(db, ings_map["Envase Kraft Eco para Postre 8oz"], "SALIDA_USO", 24.0, "unidad", "Empacado de Muffins y Postres de la semana")
            inv_service.register_movement(db, ings_map["Harina de Almendras Fina"], "SALIDA_MERMA", 150.0, "g", "Merma por rotura de bolsa al abrir")
            
            logger.info("Base de datos poblada exitosamente con registros demo.")
        else:
            logger.info("La tabla de ingredientes ya contiene registros. Saltando seed de datos.")
            
    logger.info("Base de datos inicial lista para usar.")

if __name__ == "__main__":
    seed_database()
