import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from services.inventory_service import InventoryService
from database.connection import get_db
from config.settings import CURRENCY

def render_movements():
    """
    Renderiza el módulo de Registro de Movimientos de Kárdex.
    Permite registrar Entradas (compras, reposición) y Salidas (usos, mermas, pérdidas)
    y visualizar la sábana transaccional de auditoría de inventario.
    """
    st.markdown("<h2 style='color:#AA5E5E;'>🔄 Registro de Kárdex e Historial</h2>", unsafe_allow_html=True)
    st.write("Registre entradas de compras y salidas por mermas o producción, con conversión automática de unidades.")

    inv_service = InventoryService()
    
    with get_db() as db:
        ingredients = inv_service.search_ingredients(db)
        
        # Fila doble: Registro a la izquierda y Filtros + Historial a la derecha
        col_reg, col_hist = st.columns([1, 1.3])

        # --- SECCIÓN: REGISTRAR NUEVO MOVIMIENTO (COLUMNA IZQUIERDA) ---
        with col_reg:
            st.markdown("### 📥 Registrar Transacción")
            
            if ingredients:
                with st.form("register_movement_form", clear_on_submit=True):
                    # Seleccionar ingrediente
                    ing_options = {ing.id: ing.name for ing in ingredients}
                    ing_id = st.selectbox(
                        "Seleccione Materia Prima", 
                        options=list(ing_options.keys()), 
                        format_func=lambda x: ing_options[x]
                    )
                    
                    # Obtener ingrediente seleccionado para inferir unidades
                    selected_ing = next(i for i in ingredients if i.id == ing_id)
                    
                    # Tipo de movimiento
                    type_movement = st.selectbox(
                        "Tipo de Movimiento",
                        options=[
                            "ENTRADA_COMPRA", 
                            "ENTRADA_REPOSICION", 
                            "SALIDA_USO", 
                            "SALIDA_PERDIDA", 
                            "SALIDA_MERMA"
                        ],
                        format_func=lambda x: x.replace("_", " ")
                    )
                    
                    # Unidades disponibles: Permitir unidad de compra y unidad base del ingrediente
                    unit_choices = list(set([selected_ing.unit_base, selected_ing.unit_purchase]))
                    # Si pertenecen a Peso o Volumen estándar, podemos agregar otras opciones métricas comunes
                    from services.conversion_service import ConversionService
                    fam = ConversionService.get_unit_family(selected_ing.unit_base)
                    if fam == "PESO":
                        unit_choices = list(set(unit_choices + ["g", "kg", "mg"]))
                    elif fam == "VOLUMEN":
                        unit_choices = list(set(unit_choices + ["ml", "l"]))
                        
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        quantity = st.number_input("Cantidad", min_value=0.001, value=1.0, step=1.0)
                    with col_m2:
                        unit = st.selectbox("Unidad", unit_choices, index=0)

                    # Mostrar campo de Costo del Lote SÓLO si es Entrada por Compra
                    lot_price = None
                    if type_movement == "ENTRADA_COMPRA":
                        lot_price = st.number_input(
                            f"Precio total de la Compra ({CURRENCY})", 
                            min_value=0.0, 
                            value=0.0, 
                            step=0.5,
                            help="Monto total pagado por esta compra. Se usará para actualizar el costo unitario de forma automática."
                        )
                    
                    observation = st.text_area("Observación / Notas", placeholder="Ej: Compra según factura F-02, Uso en receta Torta Matcha Proteica, Merma por derrame...")
                    
                    submit_mov = st.form_submit_button("💾 Guardar Transacción", use_container_width=True)
                    
                    if submit_mov:
                        try:
                            # Llamar al servicio de negocio
                            mov_registered = inv_service.register_movement(
                                db=db,
                                ingredient_id=ing_id,
                                type_movement=type_movement,
                                quantity=quantity,
                                unit=unit,
                                observation=observation,
                                lot_price=lot_price
                            )
                            
                            st.success(
                                f"✅ Transacción guardada. "
                                f"Se procesaron {mov_registered.quantity_base:.1f} {selected_ing.unit_base} "
                                f"en stock de {selected_ing.name}."
                            )
                            st.rerun()
                        except ValueError as e:
                            st.error(f"❌ Error de Validación: {str(e)}")
            else:
                st.warning("⚠️ Registre al menos un ingrediente en el inventario para poder registrar movimientos de stock.")

        # --- SECCIÓN: HISTORIAL Y FILTROS (COLUMNA DERECHA) ---
        with col_hist:
            st.markdown("### 📜 Filtros e Historial Kárdex")
            
            # Filtros
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                filter_ing_id = st.selectbox(
                    "Filtrar Ingrediente", 
                    options=[None] + list(ing_options.keys()) if ingredients else [None],
                    format_func=lambda x: ing_options[x] if x else "Todos los Ingredientes"
                )
            with col_f2:
                # Rango de fechas por defecto: Últimos 30 días
                date_start = st.date_input("Fecha Inicio", value=date.today() - timedelta(days=30))
                date_end = st.date_input("Fecha Fin", value=date.today())

            # Convertir fechas a objetos datetime para la base de datos
            dt_start = datetime.combine(date_start, datetime.min.time())
            dt_end = datetime.combine(date_end, datetime.max.time())
            
            # Consultar movimientos con filtros aplicando el repositorio
            from repositories.movement_repository import MovementRepository
            mov_repo = MovementRepository()
            
            if filter_ing_id:
                raw_movements = mov_repo.get_by_ingredient(db, filter_ing_id)
                # Filtrar por fecha en Python/SQL
                movements = [m for m in raw_movements if dt_start <= m.date <= dt_end]
            else:
                movements = mov_repo.get_by_date_range(db, dt_start, dt_end)

            if movements:
                # Estructurar tabla
                hist_data = []
                for m in movements:
                    ing_name = m.ingredient.name if m.ingredient else f"Ing. ID {m.ingredient_id}"
                    ing_unit_base = m.ingredient.unit_base if m.ingredient else ""
                    
                    hist_data.append({
                        "Fecha / Hora": m.date.strftime("%d/%m/%Y %H:%M:%S"),
                        "Tipo Mov.": m.type_movement.replace("_", " "),
                        "Ingrediente": ing_name,
                        "Cant. Reg.": f"{m.quantity:,.1f} {m.unit}",
                        "Equivalente Base": f"{m.quantity_base:,.1f} {ing_unit_base}",
                        "Observación": m.observation or "-"
                    })
                    
                df_hist = pd.DataFrame(hist_data)
                st.dataframe(df_hist, use_container_width=True, height=450)
            else:
                st.info("Sin registros de movimientos en el rango de fechas seleccionado.")
