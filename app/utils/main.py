
"""
SIGI Local - API Principal FastAPI
Sistema de Gestión de Incidencias con IA
"""

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.database import get_db, create_tables
from app.models.schemas import *
from app.services.database_service import DatabaseService
from app.services.ml_service import MLService
from app.api.incidents import router as incidents_router
from app.api.analysis import router as analysis_router
from app.api.dashboard import router as dashboard_router
from config.settings import settings

# Crear tablas al iniciar
create_tables()

# Inicializar FastAPI
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción restringir a dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(incidents_router, prefix="/api/incidents", tags=["incidents"])
app.include_router(analysis_router, prefix="/api/analyze", tags=["analysis"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])

@app.get("/")
async def root():
    """Endpoint raíz con información del sistema"""
    return {
        "message": "SIGI Local - Sistema de Gestión de Incidencias con IA",
        "version": settings.api_version,
        "status": "running",
        "docs": "/docs",
        "dashboard": f"http://{settings.api_host}:{settings.streamlit_port}"
    }

@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud del sistema"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "services": {
            "database": "online",
            "ml_models": "loaded",
            "api": "running"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    )
