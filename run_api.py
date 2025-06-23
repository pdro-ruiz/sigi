
#!/usr/bin/env python3
"""
Script para ejecutar solo la API FastAPI
"""

import uvicorn
from config.settings import settings

if __name__ == "__main__":
    print("🚀 Iniciando API FastAPI...")
    print(f"📍 URL: http://{settings.api_host}:{settings.api_port}")
    print(f"📖 Docs: http://{settings.api_host}:{settings.api_port}/docs")
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    )
