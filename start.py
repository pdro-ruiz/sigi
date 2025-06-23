
#!/usr/bin/env python3
"""
Script principal para iniciar SIGI Local
"""

import os
import sys
import subprocess

def main():
    """Punto de entrada principal"""
    print("🎯 SIGI Local - Sistema de Gestión de Incidencias con IA")
    print("=" * 60)
    
    # Cambiar al directorio del proyecto
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    print("📋 Verificando dependencias...")
    result = subprocess.run([sys.executable, "scripts/check_dependencies.py"])
    
    if result.returncode != 0:
        print("❌ Error en dependencias. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    print("🗄️ Verificando base de datos...")
    if not os.path.exists("data/database/sigi_local.db"):
        print("📋 Inicializando base de datos...")
        subprocess.run([sys.executable, "scripts/init_database.py"])
    
    print("🚀 Iniciando servicios...")
    subprocess.run([sys.executable, "scripts/start_services.py"])

if __name__ == "__main__":
    main()
