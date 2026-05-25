import streamlit as st
import pandas as pd
from services.auth_service import AuthService
from database.connection import get_db


def render_users():
    st.markdown("<h2 style='color:#AA5E5E;'>👥 Gestión de Usuarios</h2>", unsafe_allow_html=True)
    st.write("Cree usuarios para el equipo y administre sus accesos.")

    auth_service = AuthService()

    with get_db() as db:
        users = auth_service.get_users(db)

        if users:
            data_users = []
            for user in users:
                data_users.append({
                    "ID": user.id,
                    "Usuario": user.username,
                    "Nombre": user.name,
                    "Rol": user.role.upper(),
                    "Creado": user.created_at.strftime("%d/%m/%Y %H:%M") if user.created_at else "-"
                })
            df_users = pd.DataFrame(data_users)
            st.dataframe(df_users.set_index("ID"), use_container_width=True, height=260)
        else:
            st.info("Aun no hay usuarios registrados.")

        tab_create, tab_password = st.tabs(["➕ Crear Usuario", "🔑 Cambiar Contraseña"])

        with tab_create:
            with st.form("create_user_form"):
                col1, col2 = st.columns(2)
                with col1:
                    username = st.text_input("Usuario", placeholder="Ej: angeles")
                    full_name = st.text_input("Nombre completo", placeholder="Ej: Angeles")
                with col2:
                    password = st.text_input("Contraseña", type="password", placeholder="Mínimo 4 caracteres")
                    role = st.selectbox("Rol", ["admin", "supervisor"], index=0)

                submit_create = st.form_submit_button("Crear usuario", use_container_width=True)

                if submit_create:
                    try:
                        auth_service.create_user(
                            db=db,
                            username=username,
                            password=password,
                            name=full_name,
                            role=role
                        )
                        st.success("Usuario creado correctamente.")
                        st.rerun()
                    except ValueError as e:
                        st.error(f"❌ {str(e)}")

        with tab_password:
            if users:
                selected_user_id = st.selectbox(
                    "Seleccione usuario",
                    options=[user.id for user in users],
                    format_func=lambda uid: next((f"{u.name} ({u.username})" for u in users if u.id == uid), str(uid))
                )

                with st.form("change_password_form"):
                    new_password = st.text_input("Nueva contraseña", type="password")
                    confirm_password = st.text_input("Confirmar contraseña", type="password")
                    submit_password = st.form_submit_button("Actualizar contraseña", use_container_width=True)

                    if submit_password:
                        if new_password != confirm_password:
                            st.error("❌ Las contraseñas no coinciden.")
                        else:
                            try:
                                auth_service.update_password(db, selected_user_id, new_password)
                                st.success("Contraseña actualizada correctamente.")
                                st.rerun()
                            except ValueError as e:
                                st.error(f"❌ {str(e)}")
            else:
                st.info("No hay usuarios para editar contraseña.")
