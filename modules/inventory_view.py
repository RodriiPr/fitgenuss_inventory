import streamlit as st
import pandas as pd
from datetime import date
from services.inventory_service import InventoryService
from database.connection import get_db
from config.settings import CATEGORIES, UNITS, CURRENCY

def render_inventory():
    """
    Renderiza el módulo CRUD de gestión de ingredientes e inventario.
    Permite registrar, actualizar, buscar y eliminar materias primas.
    """
    st.markdown("<h2 style='color:#AA5E5E;'>📦 Gestión de Ingredientes (CRUD)</h2>", unsafe_allow_html=True)
    st.write("Administre su catálogo de materias primas, costos bases y especificaciones físicas.")

    inv_service = InventoryService()
    
    with get_db() as db:
        suppliers = inv_service.get_all_suppliers(db)
        supplier_options = {s.id: s.name for s in suppliers}
        
        # 1. Panel de Búsqueda y Filtros
        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            search_query = st.text_input("🔍 Buscar ingrediente...", placeholder="Buscar por nombre o categoría...", key="search_ing")
        with col_s2:
            filter_cat = st.selectbox("📁 Filtrar por Categoría", ["Todos"] + CATEGORIES, index=0)

        # Consultar ingredientes aplicando filtros
        ingredients = inv_service.search_ingredients(db, search_query, filter_cat)

        # --- SECCIÓN: TABLA INTERACTIVA DE INGREDIENTES ---
        if ingredients:
            # Crear DataFrame de Pandas para visualización ordenada
            data_list = []
            for ing in ingredients:
                total_value = ing.stock_actual * ing.costo_unitario
                status = "Normal"
                if ing.stock_actual <= ing.stock_minimo:
                    status = "🔴 Stock Mínimo"
                
                # Evaluar fecha de vencimiento
                if ing.date_expiry:
                    import datetime
                    if ing.date_expiry <= datetime.date.today():
                        status = "🚨 Vencido"
                    elif ing.date_expiry <= datetime.date.today() + datetime.timedelta(days=15):
                        status = "🟡 Prox. Vencer"
                
                data_list.append({
                    "ID": ing.id,
                    "Nombre": ing.name,
                    "Categoría": ing.category,
                    "Stock Actual": f"{ing.stock_actual:.1f} {ing.unit_base}",
                    "Stock Min.": f"{ing.stock_minimo:.1f} {ing.unit_base}",
                    "Precio Compra": f"{CURRENCY} {ing.precio_compra:.2f} / {ing.unit_purchase}",
                    "Costo Unit. (Base)": f"{CURRENCY} {ing.costo_unitario:.3f} / {ing.unit_base}",
                    "Valorizado Total": f"{CURRENCY} {total_value:.2f}",
                    "Proveedor": ing.supplier.name if ing.supplier else "-",
                    "Vencimiento": ing.date_expiry.strftime("%d/%m/%Y") if ing.date_expiry else "Sin Fecha",
                    "Estado": status
                })

            df_show = pd.DataFrame(data_list)
            st.dataframe(
                df_show.set_index("ID"),
                use_container_width=True,
                height=350
            )
        else:
            st.info("No se encontraron ingredientes con los criterios de búsqueda.")

        st.markdown("<br><hr>", unsafe_allow_html=True)

        # --- SECCIÓN: AGREGAR, EDITAR Y ELIMINAR (PANELES EXPANDIBLES) ---
        tab_add, tab_edit, tab_del, tab_supplier = st.tabs([
            "🟢 Agregar Ingrediente", 
            "🔵 Editar Ingrediente", 
            "🔴 Eliminar Ingrediente",
            "🏢 Crear Proveedor"
        ])

        # --- PESTAÑA: AGREGAR INGREDIENTE ---
        with tab_add:
            st.write("### Registrar Materia Prima Inicial")
            
            with st.form("add_ingredient_form"):
                col_a1, col_a2 = st.columns(2)
                
                with col_a1:
                    name = st.text_input("Nombre del Ingrediente", placeholder="Ej: Avena Integral, Stevia Líquida")
                    category = st.selectbox("Categoría", CATEGORIES)
                    
                    # Lógica inteligente de Unidades
                    col_u1, col_u2 = st.columns(2)
                    with col_u1:
                        unit_purchase = st.selectbox("Unidad de Compra (Lote)", ["kg", "l", "pack", "caja", "unidad", "g", "ml", "mg"])
                    with col_u2:
                        # Auto-detectar unidad base sugerida
                        default_base_idx = 0
                        if unit_purchase == "kg":
                            base_choices = ["g", "mg", "kg"]
                        elif unit_purchase == "l":
                            base_choices = ["ml", "l"]
                        elif unit_purchase in ["pack", "caja", "unidad"]:
                            base_choices = ["unidad", "pack"]
                        else:
                            base_choices = ["g", "ml", "unidad", "mg"]
                        
                        unit_base = st.selectbox("Unidad Base (Consumo)", base_choices)
                    
                    # Factor de equivalencia
                    default_factor = 1000.0 if (unit_purchase in ["kg", "l"] and unit_base in ["g", "ml"]) else 1.0
                    cantidad_compra = st.number_input("Factor de Conversión (1 Compra = N Base)", min_value=0.001, value=default_factor, step=1.0, help="Ejemplo: Si compra 1 kg y consume en gramos, coloque 1000. Si compra por unidad, coloque 1.")

                with col_a2:
                    precio_compra = st.number_input(f"Precio de Compra ({CURRENCY})", min_value=0.0, value=0.0, step=0.5, help="Precio unitario de un lote de compra.")
                    stock_minimo = st.number_input("Stock Mínimo de Alerta (Unidad Base)", min_value=0.0, value=100.0, step=10.0, help="El sistema alertará si el stock baja de esta cantidad.")
                    
                    # Seleccionar proveedor
                    if supplier_options:
                        supplier_id = st.selectbox("Proveedor", options=[None] + list(supplier_options.keys()), format_func=lambda x: supplier_options[x] if x else "Ninguno")
                    else:
                        st.warning("⚠️ No hay proveedores creados. Regístrelos en la pestaña 'Crear Proveedor'.")
                        supplier_id = None
                        
                    date_expiry = st.date_input("Fecha de Vencimiento", value=None)
                
                submit_add = st.form_submit_button("Crear Ingrediente", use_container_width=True)
                
                if submit_add:
                    if not name.strip():
                        st.error("⚠️ El nombre del ingrediente es obligatorio.")
                    elif cantidad_compra <= 0:
                        st.error("⚠️ El factor de conversión debe ser mayor que cero.")
                    else:
                        try:
                            inv_service.create_ingredient(
                                db=db,
                                name=name.strip(),
                                category=category,
                                unit_purchase=unit_purchase,
                                unit_base=unit_base,
                                cantidad_compra=cantidad_compra,
                                stock_minimo=stock_minimo,
                                precio_compra=precio_compra,
                                supplier_id=supplier_id,
                                date_purchase=date.today(),
                                date_expiry=date_expiry
                            )
                            st.success(f"🎉 ¡Ingrediente '{name}' registrado con éxito!")
                            st.rerun()
                        except ValueError as e:
                            st.error(f"❌ Error: {str(e)}")

        # --- PESTAÑA: EDITAR INGREDIENTE ---
        with tab_edit:
            st.write("### Modificar Ingrediente")
            
            if ingredients:
                ing_to_edit_id = st.selectbox(
                    "Seleccione ingrediente a editar", 
                    options=[ing.id for ing in ingredients], 
                    format_func=lambda x: next(i.name for i in ingredients if i.id == x)
                )
                
                # Obtener datos del ingrediente seleccionado
                selected_ing = next(i for i in ingredients if i.id == ing_to_edit_id)
                
                with st.form("edit_ingredient_form"):
                    col_e1, col_e2 = st.columns(2)
                    
                    with col_e1:
                        edit_name = st.text_input("Nombre", value=selected_ing.name)
                        edit_category = st.selectbox("Categoría", CATEGORIES, index=CATEGORIES.index(selected_ing.category) if selected_ing.category in CATEGORIES else 0)
                        edit_unit_purchase = st.text_input("Unidad de Compra", value=selected_ing.unit_purchase)
                        edit_unit_base = st.text_input("Unidad Base", value=selected_ing.unit_base)
                        edit_cantidad = st.number_input("Factor de Conversión", min_value=0.001, value=float(selected_ing.cantidad_compra))
                    
                    with col_e2:
                        edit_stock = st.number_input("Stock Actual Manual (Unidad Base)", min_value=0.0, value=float(selected_ing.stock_actual), help="¡Precaución! Esto altera el inventario físico directamente.")
                        edit_stock_min = st.number_input("Stock Mínimo", min_value=0.0, value=float(selected_ing.stock_minimo))
                        edit_precio = st.number_input(f"Precio Compra ({CURRENCY})", min_value=0.0, value=float(selected_ing.precio_compra))
                        
                        edit_supplier_id = st.selectbox(
                            "Proveedor", 
                            options=[None] + list(supplier_options.keys()), 
                            format_func=lambda x: supplier_options[x] if x else "Ninguno",
                            index=([None] + list(supplier_options.keys())).index(selected_ing.supplier_id) if selected_ing.supplier_id in supplier_options else 0
                        )
                        edit_expiry = st.date_input("Nueva Fecha de Vencimiento", value=selected_ing.date_expiry)

                    submit_edit = st.form_submit_button("Guardar Cambios", use_container_width=True)
                    
                    if submit_edit:
                        if not edit_name.strip():
                            st.error("⚠️ El nombre no puede estar vacío.")
                        else:
                            try:
                                inv_service.update_ingredient(
                                    db=db,
                                    ingredient_id=ing_to_edit_id,
                                    name=edit_name.strip(),
                                    category=edit_category,
                                    unit_purchase=edit_unit_purchase,
                                    unit_base=edit_unit_base,
                                    cantidad_compra=edit_cantidad,
                                    stock_actual=edit_stock,
                                    stock_minimo=edit_stock_min,
                                    precio_compra=edit_precio,
                                    supplier_id=edit_supplier_id,
                                    date_purchase=selected_ing.date_purchase,
                                    date_expiry=edit_expiry
                                )
                                st.success("🎉 ¡Ingrediente modificado correctamente!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error al actualizar: {str(e)}")
            else:
                st.info("No hay ingredientes registrados para editar.")

        # --- PESTAÑA: ELIMINAR INGREDIENTE ---
        with tab_del:
            st.write("### Eliminar Materia Prima")
            
            if ingredients:
                ing_to_del_id = st.selectbox(
                    "Seleccione ingrediente a eliminar", 
                    options=[ing.id for ing in ingredients], 
                    format_func=lambda x: next(i.name for i in ingredients if i.id == x),
                    key="del_select"
                )
                
                selected_del_ing = next(i for i in ingredients if i.id == ing_to_del_id)
                st.warning(f"⚠️ **¡CUIDADO!** Está a punto de eliminar el ingrediente **'{selected_del_ing.name}'**. Esta acción borrará de forma permanente todo su historial de Kárdex y movimientos asociados. Esta operación no se puede deshacer.")
                
                confirm_delete = st.button("❌ Confirmar Eliminar Ingrediente", use_container_width=True)
                
                if confirm_delete:
                    try:
                        inv_service.delete_ingredient(db, ing_to_del_id)
                        st.success("🎉 ¡Ingrediente eliminado del catálogo con éxito!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al eliminar: {str(e)}")
            else:
                st.info("Sin materias primas registradas.")

        # --- PESTAÑA: CREAR PROVEEDOR ---
        with tab_supplier:
            st.write("### Registrar Nuevo Proveedor")
            
            with st.form("create_supplier_form"):
                sup_name = st.text_input("Nombre de la Empresa Proveedora", placeholder="Ej: Distribuidores del Sur, Molinos Andinos")
                sup_contact = st.text_input("Nombre del Contacto / Vendedor", placeholder="Ej: Carlos Mendoza")
                
                col_s_a, col_s_b = st.columns(2)
                with col_s_a:
                    sup_phone = st.text_input("Teléfono de Contacto")
                with col_s_b:
                    sup_email = st.text_input("Correo Electrónico")
                    
                sup_address = st.text_input("Dirección Física")
                
                submit_sup = st.form_submit_button("Crear Proveedor", use_container_width=True)
                
                if submit_sup:
                    if not sup_name.strip():
                        st.error("⚠️ El nombre del proveedor es obligatorio.")
                    else:
                        try:
                            inv_service.create_supplier(
                                db=db,
                                name=sup_name.strip(),
                                contact_name=sup_contact.strip() if sup_contact else None,
                                phone=sup_phone.strip() if sup_phone else None,
                                email=sup_email.strip() if sup_email else None,
                                address=sup_address.strip() if sup_address else None
                            )
                            st.success(f"🎉 ¡Proveedor '{sup_name}' registrado con éxito!")
                            st.rerun()
                        except ValueError as e:
                            st.error(f"❌ Error: {str(e)}")
