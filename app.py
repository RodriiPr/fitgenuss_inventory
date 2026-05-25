import streamlit as st
from pathlib import Path
from database.initial_data import seed_database
from utils.styles import inject_fitgenuss_styles
from modules.login_view import render_login
from modules.dashboard_view import render_dashboard
from modules.inventory_view import render_inventory
from modules.movements_view import render_movements
from modules.alerts_view import render_alerts
from modules.reports_view import render_reports
from modules.users_view import render_users

# 1. Configuración de página de Streamlit
st.set_page_config(
    page_title="FitGenuss - Inventario Inteligente",
    page_icon="🍰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inicializar base de datos y sembrar datos demo de forma automática y segura
@st.cache_resource
def startup_db():
    """Ejecuta la inicialización de base de datos una sola vez en el arranque."""
    seed_database()

startup_db()

# 3. Inyectar estilos personalizados premium de FitGenuss
inject_fitgenuss_styles()

# 4. Inicializar estados de sesión para control de flujo y autenticación
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None

# 5. CONTROL DE ACCESO / AUTENTICACIÓN
if not st.session_state.authenticated:
    # Renderiza la pantalla de Login y detiene la ejecución
    render_login()
else:
    # 6. PANEL DE CONTROL ADMINISTRATIVO (Sidebar de navegación)
    with st.sidebar:
        logo_path = Path(__file__).resolve().parent / "assets" / "logo_fitgenuss_principal.jpeg"
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)

        # Título decorativo
        st.markdown("<h2 style='text-align: center; color: #AA5E5E; margin-bottom: 0;'>FitGenuss</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #6F6A63; font-size: 0.85rem; margin-top:0;'>ERP & Inventario de Postres Fit</p>", unsafe_allow_html=True)
        st.markdown("<hr style='margin-top:0;'>", unsafe_allow_html=True)
        
        # Ficha del perfil del usuario logueado
        user_info = st.session_state.user
        st.markdown(f"""
        <div style='padding: 10px; border-radius: 8px; background-color: #FFFFFF; border: 1px solid #E2E8F0; margin-bottom: 15px;'>
            <span style='font-size:0.75rem; color:#94A3B8; text-transform:uppercase; font-weight:600;'>Usuario Activo</span><br>
            <strong style='color:#1E293B;'>👤 {user_info['name']}</strong><br>
            <span class='badge badge-success' style='font-size: 0.65rem; margin-top:4px;'>Rol: {user_info['role'].upper()}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🧭 Menú Principal")
        
        # Opciones de Navegación del ERP
        menu_selection = st.radio(
            "Seleccione un módulo:",
            options=[
                "📊 Dashboard Ejecutivo",
                "📦 Catálogo de Ingredientes",
                "🔄 Kárdex de Movimientos",
                "🔔 Centro de Alertas",
                "👥 Gestión de Usuarios",
                "📋 Reportes y Backup"
            ],
            index=0,
            label_visibility="collapsed"
        )
        
        st.markdown("<br><br><hr>", unsafe_allow_html=True)
        
        # Botón de Cerrar Sesión
        logout_btn = st.button("🚪 Cerrar Sesión", use_container_width=True)
        if logout_btn:
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()

    # 7. ROUTING / RENDERIZAR VISTAS DILIGENCIADAS
    if menu_selection == "📊 Dashboard Ejecutivo":
        render_dashboard()
        
    elif menu_selection == "📦 Catálogo de Ingredientes":
        render_inventory()
        
    elif menu_selection == "🔄 Kárdex de Movimientos":
        render_movements()
        
    elif menu_selection == "🔔 Centro de Alertas":
        render_alerts()

    elif menu_selection == "👥 Gestión de Usuarios":
        render_users()
         
    elif menu_selection == "📋 Reportes y Backup":
        render_reports()
