
#!/usr/bin/env python3
"""
Script para ejecutar solo el dashboard Streamlit
"""

import subprocess
import sys
from config.settings import settings

if __name__ == "__main__":
    print("📊 Iniciando Dashboard Streamlit...")
    print(f"📍 URL: http://{settings.api_host}:{settings.streamlit_port}")
    
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "frontend/dashboard.py",
        "--server.port", str(settings.streamlit_port),
        "--server.address", settings.api_host
    ])
