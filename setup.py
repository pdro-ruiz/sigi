
#!/usr/bin/env python3
"""
SIGI Local - Sistema de Gestión de Incidencias con IA
Script de instalación y configuración automática
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def install_requirements():
    """Instala las dependencias del proyecto"""
    print("📦 Instalando dependencias...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("✅ Dependencias instaladas correctamente")

def download_ml_models():
    """Descarga los modelos de ML necesarios"""
    print("🤖 Descargando modelos de Machine Learning...")
    
    # Descargar modelo de spaCy en español
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "es_core_news_sm"])
    
    # Los modelos de transformers se descargarán automáticamente en el primer uso
    print("✅ Modelos de ML configurados")

def setup_database():
    """Inicializa la base de datos SQLite"""
    print("🗄️ Configurando base de datos...")
    
    db_path = Path("data/database/sigi_local.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Crear tablas básicas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            category VARCHAR(100),
            priority VARCHAR(50),
            status VARCHAR(50) DEFAULT 'open',
            sentiment_score FLOAT,
            urgency_level VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            assigned_to VARCHAR(100),
            resolved_at TIMESTAMP,
            resolution_notes TEXT,
            duplicate_of INTEGER,
            FOREIGN KEY (duplicate_of) REFERENCES incidents(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Base de datos configurada")

def create_config_files():
    """Crea archivos de configuración"""
    print("⚙️ Creando archivos de configuración...")
    
    config_content = """
# SIGI Local Configuration
DATABASE_URL=sqlite:///data/database/sigi_local.db
API_HOST=127.0.0.1
API_PORT=8000
STREAMLIT_PORT=8501
ML_MODEL_PATH=data/models/
LOG_LEVEL=INFO
"""
    
    with open("config/.env", "w") as f:
        f.write(config_content)
    
    print("✅ Configuración creada")

def main():
    """Función principal de instalación"""
    print("🚀 Iniciando instalación de SIGI Local...")
    print("=" * 50)
    
    try:
        install_requirements()
        download_ml_models()
        setup_database()
        create_config_files()
        
        print("=" * 50)
        print("✅ SIGI Local instalado correctamente!")
        print("\nPara iniciar el sistema:")
        print("1. API FastAPI: python -m app.main")
        print("2. Dashboard Streamlit: streamlit run frontend/dashboard.py")
        print("\nAcceso:")
        print("- API: http://localhost:8000")
        print("- Dashboard: http://localhost:8501")
        print("- Documentación API: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"❌ Error durante la instalación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
