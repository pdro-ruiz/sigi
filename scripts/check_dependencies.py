
#!/usr/bin/env python3
"""
Script para verificar que todas las dependencias estén instaladas correctamente
"""

import sys
import importlib

REQUIRED_PACKAGES = [
    'fastapi',
    'uvicorn',
    'streamlit',
    'pandas',
    'numpy',
    'plotly',
    'requests',
    'sqlalchemy',
    'pydantic'
]

OPTIONAL_PACKAGES = [
    'transformers',
    'torch',
    'spacy',
    'nltk',
    'scikit-learn'
]

def check_package(package_name):
    """Verificar si un paquete está instalado"""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def main():
    """Verificar todas las dependencias"""
    print("📦 Verificando dependencias de SIGI Local...")
    print("=" * 50)
    
    all_good = True
    
    # Verificar paquetes requeridos
    print("✅ Paquetes requeridos:")
    for package in REQUIRED_PACKAGES:
        if check_package(package):
            print(f"   ✓ {package}")
        else:
            print(f"   ❌ {package} - NO INSTALADO")
            all_good = False
    
    print("\n🤖 Paquetes de ML (opcionales):")
    ml_packages_available = 0
    for package in OPTIONAL_PACKAGES:
        if check_package(package):
            print(f"   ✓ {package}")
            ml_packages_available += 1
        else:
            print(f"   ⚠️ {package} - no disponible (funcionará con implementación básica)")
    
    print("\n" + "=" * 50)
    
    if all_good:
        print("✅ Todas las dependencias requeridas están instaladas")
        if ml_packages_available >= 3:
            print("🤖 Funcionalidades ML avanzadas disponibles")
        else:
            print("🔧 Funcionará con implementaciones básicas de ML")
        return True
    else:
        print("❌ Faltan dependencias requeridas. Ejecuta:")
        print("   pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
