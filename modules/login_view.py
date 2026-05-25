import streamlit as st
from pathlib import Path
from services.auth_service import AuthService
from database.connection import get_db

def render_login():
    """
    Renderiza la vista de inicio de sesión de FitGenuss.
    Utiliza estilos premium centrados y tarjetas de vidrio.
    """
    logo_path = Path(__file__).resolve().parents[1] / "assets" / "logo_fitgenuss_principal.jpeg"
    if logo_path.exists():
        col_logo_l, col_logo_c, col_logo_r = st.columns([1, 1.2, 1])
        with col_logo_c:
            st.image(str(logo_path), use_container_width=True)

    st.markdown("""
    <div class='fg-login-intro'>
        <span class='fg-login-chip'>FITGENUSS PROTEIN DESSERTS</span>
        <h1 class='fg-login-title'>Acceso al ERP de Inventario</h1>
        <p class='fg-login-subtitle'>Monitorea stock, movimientos y alertas con una experiencia alineada a tu marca.</p>
        <div class='fg-login-features'>
            <span>Alto en proteina</span>
            <span>Sin gluten</span>
            <span>Sin azucar anadida</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Crear columnas para centrar la tarjeta de login
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Formulario de inicio de sesión
        with st.form("login_form", clear_on_submit=False):
            st.markdown("<div class='login-form-title'>🔐 Acceso administrativo</div>", unsafe_allow_html=True)
            
            username = st.text_input("Usuario", placeholder="Ej: andre o angeles", key="login_username")
            password = st.text_input("Contrasena", type="password", placeholder="Ingrese su contrasena", key="login_password")
            
            submit_btn = st.form_submit_button("Ingresar al sistema", use_container_width=True)
            
            if submit_btn:
                if not username or not password:
                    st.error("⚠️ Por favor complete todos los campos.")
                else:
                    auth_service = AuthService()
                    with get_db() as db:
                        user = auth_service.authenticate(db, username, password)
                        if user:
                            # Establecer sesión activa
                            st.session_state.authenticated = True
                            st.session_state.user = {
                                "id": user.id,
                                "username": user.username,
                                "name": user.name,
                                "role": user.role
                            }
                            st.success(f"¡Bienvenido, {user.name}!")
                            st.rerun()
                        else:
                            st.error("❌ Usuario o contraseña incorrectos. Intente nuevamente.")
                            
        st.markdown('</div>', unsafe_allow_html=True)
