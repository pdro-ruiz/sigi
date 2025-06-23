
#!/usr/bin/env python3
"""
Script para iniciar todos los servicios de SIGI Local
"""

import subprocess
import sys
import os
import time
import signal
from threading import Thread

def start_api_server():
    """Iniciar servidor FastAPI"""
    print("🚀 Iniciando servidor API FastAPI...")
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "127.0.0.1", 
            "--port", "8000",
            "--reload"
        ], cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    except KeyboardInterrupt:
        print("🛑 Servidor API detenido")

def start_streamlit_dashboard():
    """Iniciar dashboard Streamlit"""
    print("📊 Iniciando dashboard Streamlit...")
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "frontend/dashboard.py",
            "--server.port", "8501",
            "--server.address", "127.0.0.1"
        ], cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    except KeyboardInterrupt:
        print("🛑 Dashboard detenido")

def main():
    """Función principal para iniciar ambos servicios"""
    print("🎯 SIGI Local - Iniciando sistema completo...")
    print("=" * 50)
    
    # Verificar que la base de datos esté inicializada
    from scripts.init_database import init_database
    if not os.path.exists("data/database/sigi_local.db"):
        print("📋 Base de datos no encontrada. Inicializando...")
        init_database()
    
    try:
        # Iniciar API en thread separado
        api_thread = Thread(target=start_api_server, daemon=True)
        api_thread.start()
        
        # Esperar un poco para que la API se inicie
        time.sleep(3)
        
        print("✅ Servicios iniciados correctamente!")
        print("🔗 URLs de acceso:")
        print("   - API FastAPI: http://127.0.0.1:8000")
        print("   - Documentación API: http://127.0.0.1:8000/docs")
        print("   - Dashboard Streamlit: http://127.0.0.1:8501")
        print("\n💡 Presiona Ctrl+C para detener los servicios")
        
        # Iniciar Streamlit en proceso principal
        start_streamlit_dashboard()
        
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servicios...")
        print("✅ SIGI Local detenido correctamente")

if __name__ == "__main__":
    main()
