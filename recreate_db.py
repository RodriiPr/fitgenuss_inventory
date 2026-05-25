import sys
from database.connection import engine, Base
import models

def clean_and_rebuild_database():
    """
    Script de utilidad para borrar tablas huérfanas o antiguas en la base de datos
    (SQLite o Aiven PostgreSQL) y reconstruirlas con las columnas correctas.
    """
    print("=" * 70)
    print("🧹 ASISTENTE DE MIGRACIÓN Y LIMPIEZA DE BASE DE DADOS - FITGENUSS")
    print("=" * 70)
    print("¡ATENCIÓN! Este script eliminará de forma permanente todas las tablas")
    print("existentes en la base de datos configurada en tu archivo .env")
    print("y las volverá a crear con la estructura de columnas limpia y actualizada.")
    print("-" * 70)
    
    # Mostrar la base de datos de destino
    db_name = "PostgreSQL en Aiven" if "aiven" in str(engine.url) else "SQLite Local"
    print(f"🎯 Base de datos objetivo: {db_name}")
    print(f"🔗 URL: {engine.url.render_as_string(hide_password=True)}")
    print("-" * 70)
    
    # Confirmación de seguridad
    confirm = input("¿Estás seguro de que deseas continuar? Se borrarán datos antiguos (s/n): ")
    
    if confirm.strip().lower() == 's':
        print("\n🗑️  Eliminando tablas antiguas de la base de datos...")
        try:
            Base.metadata.drop_all(bind=engine)
            print("✅ Tablas eliminadas correctamente.")
            
            print("\n🏗️  Creando nuevas tablas con la estructura limpia y actualizada...")
            Base.metadata.create_all(bind=engine)
            print("✅ ¡Estructura de tablas creada con éxito!")
            
            print("\n🎉 La base de datos ya está lista. Puedes iniciar 'streamlit run app.py' para arrancar.")
        except Exception as e:
            print(f"\n❌ Error al interactuar con la base de datos: {str(e)}")
            print("Asegúrate de que tu URL en el archivo .env sea correcta y que tu base de datos en la nube esté activa.")
    else:
        print("\n❌ Operación cancelada por el usuario. No se realizaron cambios.")
        sys.exit(0)

if __name__ == "__main__":
    clean_and_rebuild_database()
