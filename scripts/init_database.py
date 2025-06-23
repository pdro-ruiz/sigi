
#!/usr/bin/env python3
"""
Script para inicializar la base de datos SIGI Local
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import create_tables, engine
from scripts.seed_data import create_sample_data

def init_database():
    """Inicializar base de datos con esquema y datos de ejemplo"""
    print("🗄️ Inicializando base de datos SIGI Local...")
    
    try:
        # Crear todas las tablas
        print("📋 Creando esquemas de base de datos...")
        create_tables()
        print("✅ Esquemas creados correctamente")
        
        # Crear datos de ejemplo
        print("🌱 Cargando datos de ejemplo...")
        create_sample_data()
        print("✅ Datos de ejemplo cargados")
        
        print("🎉 Base de datos inicializada correctamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error inicializando base de datos: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
