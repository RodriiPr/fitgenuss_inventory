import streamlit as st
import datetime
from services.inventory_service import InventoryService
from database.connection import get_db

def render_alerts():
    """
    Renderiza la vista del Centro de Alertas Críticas de FitGenuss.
    Consolida advertencias de stock mínimo y caducidad de ingredientes.
    """
    st.markdown("<h2 style='color:#AA5E5E;'>🔔 Centro de Alertas y Abastecimiento</h2>", unsafe_allow_html=True)
    st.write("Monitoree los ingredientes en estado crítico de stock y lotes próximos a vencer para asegurar la producción fit.")

    inv_service = InventoryService()
    
    with get_db() as db:
        low_stock = inv_service.get_low_stock_alerts(db)
        expiring = inv_service.get_expiring_alerts(db)
        
        tab_stock, tab_expiry = st.tabs([
            f"🔴 Quiebre de Stock ({len(low_stock)})", 
            f"🚨 Vencimientos y Caducidad ({len(expiring)})"
        ])
        
        # --- PESTAÑA: QUIEBRE DE STOCK ---
        with tab_stock:
            st.markdown("### ⚠️ Ingredientes por debajo del Stock Mínimo")
            st.write("Los siguientes ingredientes requieren reabastecimiento urgente para no frenar la cocina saludable:")
            
            if low_stock:
                for ing in low_stock:
                    # Calcular porcentaje de stock actual vs mínimo para barra de progreso
                    percentage = (ing.stock_actual / ing.stock_minimo) if ing.stock_minimo > 0 else 0.0
                    percentage = min(percentage, 1.0) # Cap al 100%
                    
                    st.markdown(f"""
                    <div style='padding: 20px; border-radius: 12px; border: 1px solid #FCA5A5; background-color: #FEF2F2; margin-bottom: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.02);'>
                        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                            <strong style='color: #B91C1C; font-size: 1.15rem; font-family: Outfit, sans-serif;'>{ing.name}</strong>
                            <span class='badge' style='background-color: #EF4444; color: white;'>Reponer Urgente</span>
                        </div>
                        <div style='font-size: 0.9rem; color: #7F1D1D; margin-bottom: 12px;'>
                            Categoría: <b>{ing.category}</b> | Proveedor: <b>{ing.supplier.name if ing.supplier else 'Sin Asignar'}</b><br>
                            Stock Físico Actual: <strong style='font-size:1.1rem;'>{ing.stock_actual:.1f} {ing.unit_base}</strong> | Umbral Mínimo: <b>{ing.stock_minimo:.1f} {ing.unit_base}</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Barra de progreso visual nativa de Streamlit
                    st.progress(percentage, text=f"Porcentaje de Abastecimiento: {percentage * 100:.1f}%")
                    
                    # Botón rápido para contactar al proveedor
                    if ing.supplier:
                        col_btn1, col_btn2 = st.columns([1, 3])
                        with col_btn1:
                            subject = f"Pedido urgente de FitGenuss: {ing.name}"
                            body = f"Estimado {ing.supplier.contact_name or 'Proveedor'},\n\nRequerimos abastecimiento urgente para el ingrediente '{ing.name}' debido a un nivel crítico de stock en nuestro inventario.\n\nQuedamos atentos a la cotización y tiempo de entrega.\n\nSaludos,\nAdministrador de FitGenuss."
                            # Codificar enlace mailto
                            import urllib.parse
                            mail_link = f"mailto:{ing.supplier.email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
                            st.markdown(f"""
                            <a href="{mail_link}" style="text-decoration:none;">
                                <button style="background-color:#EF4444; color:white; border:none; padding:8px 12px; border-radius:6px; font-weight:600; font-size:0.8rem; cursor:pointer;">
                                    📧 Contactar por Email
                                </button>
                            </a>
                            """, unsafe_allow_html=True)
                    st.markdown("<hr style='border: 0.5px solid #F3F4F6;'>", unsafe_allow_html=True)
            else:
                st.success("🎉 ¡Felicidades! Todas las materias primas disponen de un volumen de stock seguro y fuera de peligro.")

        # --- PESTAÑA: ALERTAS DE CADUCIDAD ---
        with tab_expiry:
            st.markdown("### 🚨 Control de Fechas de Vencimiento de Lotes")
            st.write("Monitoree los lotes de ingredientes perecederos que vencieron o que caducarán en los próximos días:")
            
            if expiring:
                for ing in expiring:
                    days_remaining = (ing.date_expiry - datetime.date.today()).days
                    
                    if days_remaining < 0:
                        status_text = f"🚨 VENCIDO HACE {-days_remaining} DÍAS"
                        color_border = "#B91C1C"
                        color_bg = "#FEF2F2"
                        color_text = "#991B1B"
                        badge_style = "background-color: #EF4444; color: white;"
                    elif days_remaining == 0:
                        status_text = "🚨 VENCE HOY"
                        color_border = "#EA580C"
                        color_bg = "#FFF7ED"
                        color_text = "#C2410C"
                        badge_style = "background-color: #F97316; color: white;"
                    else:
                        status_text = f"🟡 Vence en {days_remaining} días"
                        color_border = "#D97706"
                        color_bg = "#FFFBEB"
                        color_text = "#92400E"
                        badge_style = "background-color: #F59E0B; color: white;"
                        
                    st.markdown(f"""
                    <div style='padding: 20px; border-radius: 12px; border: 1px solid {color_border}; background-color: {color_bg}; margin-bottom: 16px;'>
                        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                            <strong style='color: {color_text}; font-size: 1.15rem; font-family: Outfit, sans-serif;'>{ing.name}</strong>
                            <span class='badge' style='{badge_style}'>{status_text}</span>
                        </div>
                        <div style='font-size: 0.9rem; color: {color_text}EE;'>
                            Categoría: <b>{ing.category}</b> | Stock Actual: <b>{ing.stock_actual:.1f} {ing.unit_base}</b><br>
                            Fecha de Caducidad Registrada: <strong style='font-size:1.05rem;'>{ing.date_expiry.strftime('%d/%m/%Y')}</strong>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("🎉 ¡Excelente! No existen ingredientes vencidos ni próximos a vencer en el período configurado.")
