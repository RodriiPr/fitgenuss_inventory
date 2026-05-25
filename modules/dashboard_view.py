import streamlit as st
import pandas as pd
import plotly.express as px
from services.inventory_service import InventoryService
from database.connection import get_db
from utils.styles import render_kpi_card
from config.settings import CURRENCY

def render_dashboard():
    """
    Renderiza el Dashboard ejecutivo de FitGenuss.
    Muestra KPIs monetarios y de alertas, así como gráficos interactivos de Plotly.
    """
    # 1. Banner Principal Corporativo
    st.markdown("""
    <div class="fitgenuss-banner">
        <h1>Control de Inventario FitGenuss</h1>
        <p>Monitoreo inteligente de materias primas, costos e ingredientes saludables para la elaboración de postres fit premium en tiempo real.</p>
    </div>
    """, unsafe_allow_html=True)

    inv_service = InventoryService()
    
    with get_db() as db:
        # Consultar datos y KPIs del servicio de negocio
        kpis = inv_service.get_dashboard_kpis(db)
        recent_movements = inv_service.get_recent_movements(db, limit=5)
        low_stock_list = inv_service.get_low_stock_alerts(db)
        expiring_list = inv_service.get_expiring_alerts(db)
        ingredients = inv_service.search_ingredients(db)

        # 2. Renderizar Fila de Tarjetas KPI
        col1, col2, col3, col4 = st.columns(4)
        render_kpi_card("Total Ingredientes", f"{kpis['total_ingredients']} ítems", col1)
        render_kpi_card("Valor de Inventario", f"{CURRENCY} {kpis['total_valuation']:,.2f}", col2)
        render_kpi_card("Stock Mínimo Crítico", f"{kpis['low_stock_count']} alertas", col3)
        render_kpi_card("Próximos a Vencer", f"{kpis['expiring_count']} alertas", col4)

        st.markdown("<br>", unsafe_allow_html=True)

        # 3. Gráficos Interactivos de Plotly
        st.subheader("📊 Análisis y Estadísticas de Stock")
        
        if ingredients:
            col_chart1, col_chart2 = st.columns(2)
            
            # Preparar datos para los gráficos
            df_ing = pd.DataFrame([{
                "name": ing.name,
                "category": ing.category,
                "stock": ing.stock_actual,
                "unit": ing.unit_base,
                "valuation": ing.stock_actual * ing.costo_unitario
            } for ing in ingredients])

            with col_chart1:
                st.write("**Valorización de Stock por Categoría**")
                # Gráfico de Dona de Valorización por Categoría
                df_cat = df_ing.groupby("category")["valuation"].sum().reset_index()
                if df_cat["valuation"].sum() > 0:
                    fig_pie = px.pie(
                        df_cat, 
                        values="valuation", 
                        names="category", 
                        hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Prism
                    )
                    fig_pie.update_layout(
                        margin=dict(t=10, b=10, l=10, r=10),
                        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                        height=320
                    )
                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("Sin stock valorizado suficiente para graficar.")

            with col_chart2:
                st.write("**Top 10 Ingredientes con Mayor Stock (Unidad Base)**")
                # Gráfico de barras de top 10 ingredientes por stock actual
                df_top = df_ing.sort_values(by="stock", ascending=False).head(10)
                if df_top["stock"].sum() > 0:
                    fig_bar = px.bar(
                        df_top,
                        x="stock",
                        y="name",
                        orientation="h",
                        labels={"stock": "Cantidad en Stock", "name": "Ingrediente"},
                        color="category",
                        color_discrete_sequence=px.colors.qualitative.Pastel
                    )
                    fig_bar.update_layout(
                        margin=dict(t=10, b=10, l=10, r=10),
                        showlegend=False,
                        height=320,
                        yaxis={'categoryorder':'total ascending'}
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                else:
                    st.info("Registra entradas de stock para visualizar este gráfico.")
        else:
            st.info("Registre sus primeros ingredientes para activar los gráficos de análisis de inventario.")

        st.markdown("<br><hr>", unsafe_allow_html=True)

        # 4. Sección de Alertas y Movimientos Recientes
        col_list1, col_list2 = st.columns([1, 1.2])

        with col_list1:
            st.markdown("### 🔔 Centro de Alertas Críticas")
            
            tab_stock, tab_exp = st.tabs(["Stock Bajo", "Próximo a Vencer / Vencido"])
            
            with tab_stock:
                if low_stock_list:
                    for ing in low_stock_list:
                        st.markdown(f"""
                        <div style='padding: 10px; border-left: 4px solid #EF4444; background-color: #FEF2F2; border-radius: 4px; margin-bottom: 8px;'>
                            <strong style='color:#B91C1C;'>{ing.name}</strong><br>
                            <span style='font-size:0.85rem; color:#7F1D1D;'>
                                Categoría: {ing.category} | <b>Stock: {ing.stock_actual:.1f} {ing.unit_base}</b> (Mínimo: {ing.stock_minimo:.1f} {ing.unit_base})
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("✅ Todos los ingredientes disponen de stock suficiente.")
                    
            with tab_exp:
                if expiring_list:
                    for ing in expiring_list:
                        # Evaluar si está vencido o próximo a vencer
                        import datetime
                        vencido = ing.date_expiry <= datetime.date.today()
                        color = "#EF4444" if vencido else "#F59E0B"
                        bg = "#FEF2F2" if vencido else "#FFFBEB"
                        text_col = "#B91C1C" if vencido else "#B45309"
                        label = "VENCIDO" if vencido else "PRÓXIMO A VENCER"
                        
                        st.markdown(f"""
                        <div style='padding: 10px; border-left: 4px solid {color}; background-color: {bg}; border-radius: 4px; margin-bottom: 8px;'>
                            <strong style='color:{text_col};'>{ing.name}</strong> 
                            <span class='badge' style='background-color:{color}22; color:{color}; padding:2px 6px; font-size:0.7rem;'>{label}</span><br>
                            <span style='font-size:0.85rem; color:{text_col}CC;'>
                                Vence el: <b>{ing.date_expiry.strftime('%d/%m/%Y')}</b> | Stock: {ing.stock_actual:.1f} {ing.unit_base}
                            </span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("✅ Sin alertas de caducidad en sus materias primas.")

        with col_list2:
            st.markdown("### 🔄 Historial Reciente de Kárdex")
            
            if recent_movements:
                data_movements = []
                for mov in recent_movements:
                    ing_name = mov.ingredient.name if mov.ingredient else f"ID {mov.ingredient_id}"
                    movement_type = "Entrada" if "ENTRADA" in mov.type_movement else "Salida"
                    data_movements.append({
                        "Fecha": mov.date.strftime("%d/%m %H:%M"),
                        "Tipo": movement_type,
                        "Ingrediente": ing_name,
                        "Cantidad": f"{mov.quantity:,.1f} {mov.unit}"
                    })

                df_movements = pd.DataFrame(data_movements)
                st.dataframe(df_movements, use_container_width=True, hide_index=True, height=290)
            else:
                st.info("Sin registros de movimientos en el Kárdex de stock.")
