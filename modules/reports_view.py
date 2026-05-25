import streamlit as st
import os
import shutil
from datetime import datetime
from services.report_service import ReportService
from database.connection import get_db
from config.settings import BASE_DIR, DB_FILE_PATH

def render_reports():
    """
    Renderiza el panel de descargas de reportes ejecutivos en PDF/Excel
    y copias de seguridad de la base de datos de FitGenuss.
    """
    st.markdown("<h2 style='color:#AA5E5E;'>📋 Reportes y Copias de Seguridad</h2>", unsafe_allow_html=True)
    st.write("Exporte reportes listos para auditorías o guarde respaldos manuales de su base de datos.")

    report_service = ReportService()
    
    col_rep, col_back = st.columns(2)

    # --- SECCIÓN: EXPORTACIÓN DE REPORTES (COLUMNA IZQUIERDA) ---
    with col_rep:
        st.markdown("### 📥 Descargar Reportes en PDF y Excel")
        st.write("Descargue la información de su stock actual u historial de Kárdex estructurado y formateado:")
        
        with get_db() as db:
            # 1. Reporte de Inventario Actual
            st.markdown("---")
            st.write("📊 **Reporte de Inventario Actual Valorizado**")
            
            # Generar datos binarios
            try:
                excel_inv = report_service.generate_inventory_excel(db)
                pdf_inv = report_service.generate_inventory_pdf(db)
                
                col_e_inv, col_p_inv = st.columns(2)
                with col_e_inv:
                    st.download_button(
                        label="🟢 Descargar Excel",
                        data=excel_inv,
                        file_name=f"fitgenuss_inventario_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                with col_p_inv:
                    st.download_button(
                        label="🔴 Descargar PDF",
                        data=pdf_inv,
                        file_name=f"fitgenuss_inventario_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"Error al preparar reportes de inventario: {str(e)}")

            # 2. Reporte de Kárdex de Movimientos
            st.markdown("---")
            st.write("🔄 **Kárdex de Movimientos Histórico**")
            
            try:
                excel_mov = report_service.generate_movements_excel(db)
                pdf_mov = report_service.generate_movements_pdf(db)
                
                col_e_mov, col_p_mov = st.columns(2)
                with col_e_mov:
                    st.download_button(
                        label="🟢 Descargar Excel",
                        data=excel_mov,
                        file_name=f"fitgenuss_kardex_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                with col_p_mov:
                    st.download_button(
                        label="🔴 Descargar PDF",
                        data=pdf_mov,
                        file_name=f"fitgenuss_kardex_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"Error al preparar reportes de Kárdex: {str(e)}")

    # --- SECCIÓN: COPIA DE SEGURIDAD (COLUMNA DERECHA) ---
    with col_back:
        st.markdown("### 💾 Copia de Seguridad y Backups")
        st.write("Proteja su base de datos. Guarde copias de seguridad de forma local en la aplicación o descárguelas directamente en su equipo:")
        
        st.markdown("---")
        
        # Evaluar tipo de base de datos
        if DB_FILE_PATH.exists():
            st.info("ℹ️ Su base de datos está configurada en **SQLite** local. Puede clonar el archivo de base de datos de inmediato.")
            
            # Crear directorio de backups si no existe
            backup_dir = BASE_DIR / "assets" / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Botón de backup local
            trigger_backup = st.button("🗄️ Generar Copia de Seguridad Local", use_container_width=True)
            
            if trigger_backup:
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_filename = f"fitgenuss_backup_{timestamp}.db"
                    backup_path = backup_dir / backup_filename
                    
                    # Copia caliente de archivo
                    shutil.copy2(DB_FILE_PATH, backup_path)
                    st.success(f"🎉 ¡Copia de seguridad local creada con éxito!\nGuardada en: `assets/backups/{backup_filename}`")
                except Exception as e:
                    st.error(f"❌ Error al realizar backup local: {str(e)}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.write("🔽 **Descargar base de datos actual en caliente (.db):**")
            
            # Botón de descarga de base de datos directa
            try:
                with open(DB_FILE_PATH, "rb") as db_file:
                    db_bytes = db_file.read()
                    
                st.download_button(
                    label="💾 Descargar Base de Datos .db",
                    data=db_bytes,
                    file_name=f"fitgenuss_db_{datetime.now().strftime('%Y%m%d_%H%M')}.db",
                    mime="application/x-sqlite3",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error al leer la base de datos para descarga: {str(e)}")
        else:
            st.warning("⚠️ La base de datos local SQLite no se encuentra activa, o está utilizando PostgreSQL remoto en la nube. Las copias de seguridad calientes automatizadas por archivo directo están inhabilitadas en este modo de conexión.")
